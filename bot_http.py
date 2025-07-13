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

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://safeguard-bot.vercel.app')
LOCAL_DEV = os.getenv('LOCAL_DEV', 'false').lower() == 'true'

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
                
                # Send welcome message
                welcome_text = f"""
                    👋 Welcome {new_member.get('first_name', 'User')} to the group!

                    🔐 <b>SAFE GUARD BOT</b> is here to help you verify your account.

                    <i>Click the button below to start verification</i>
                    """
                
                # For local development, don't use inline keyboard (Telegram requires HTTPS)
                print(f"🔧 LOCAL_DEV setting: {LOCAL_DEV}")
                print(f"🔧 WEBAPP_URL: {WEBAPP_URL}")
                
                if LOCAL_DEV:
                    # Send message without inline keyboard for local testing
                    welcome_text += f"\n\n🌐 <b>Local Development Mode</b>\nPlease visit: {WEBAPP_URL}"
                    keyboard = None
                    print(f"🔧 Using LOCAL_DEV mode - no inline keyboard")
                else:
                    keyboard = {
                        "inline_keyboard": [[
                            {
                                "text": "🔐 Start Verification",
                                "url": WEBAPP_URL
                            }
                        ]]
                    }
                    print(f"🔧 Using PRODUCTION mode - with inline keyboard")
                
                try:
                    result = self.send_message(
                        chat_id=chat['id'],
                        text=welcome_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                    
                    if result:
                        logger.info(f"✅ Welcome message sent for new member {new_member.get('id')} in chat {chat.get('id')}")
                    else:
                        logger.error(f"❌ Failed to send welcome message")
                        
                except Exception as e:
                    logger.error(f"❌ Error sending welcome message: {e}")
            else:
                logger.info(f"🤖 Skipping bot member: {new_member.get('first_name')}")

    def handle_message(self, message):
        """Handle regular text messages"""
        user = message.get('from', {})
        chat = message.get('chat', {})
        text = message.get('text', '')
        
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
            logger.info("💡 Make sure the bot is added to groups with proper permissions")
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