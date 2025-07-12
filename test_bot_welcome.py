#!/usr/bin/env python3
"""
Test Script for Bot Welcome Messages

This script simulates new users joining a group to test the bot's welcome message functionality.
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
TEST_CHAT_ID = os.getenv('TEST_CHAT_ID')  # Add your test group chat ID to .env
TEST_USER_ID = os.getenv('TEST_USER_ID')  # Add your test user ID to .env

def get_bot_info():
    """Get bot information"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"🤖 Bot Info:")
            print(f"   Name: {bot_info['first_name']}")
            print(f"   Username: @{bot_info['username']}")
            print(f"   ID: {bot_info['id']}")
            return bot_info
        else:
            print(f"❌ Failed to get bot info: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return None

def get_chat_info(chat_id):
    """Get chat information"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getChat", 
                              params={'chat_id': chat_id})
        if response.status_code == 200:
            chat_info = response.json()['result']
            print(f"💬 Chat Info:")
            print(f"   Title: {chat_info.get('title', 'Private Chat')}")
            print(f"   Type: {chat_info['type']}")
            print(f"   ID: {chat_info['id']}")
            return chat_info
        else:
            print(f"❌ Failed to get chat info: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting chat info: {e}")
        return None

def test_welcome_message(chat_id, user_name="Test User"):
    """Test sending a welcome message to simulate new user joining"""
    try:
        # Create a mock welcome message
        welcome_text = f"""
👋 Welcome {user_name} to the group!

🔐 <b>SAFE GUARD BOT</b> is here to help you verify your account.

<i>Click the button below to start verification</i>
"""
        
        # Create inline keyboard
        keyboard = {
            "inline_keyboard": [[
                {
                    "text": "🔐 Start Verification",
                    "url": os.getenv('WEBAPP_URL', 'http://localhost:5000')
                }
            ]]
        }
        
        # Send the message
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": welcome_text,
                "reply_markup": keyboard,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()['result']
            print(f"✅ Welcome message sent successfully!")
            print(f"   Message ID: {result['message_id']}")
            print(f"   Chat ID: {result['chat']['id']}")
            return True
        else:
            print(f"❌ Failed to send welcome message: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending welcome message: {e}")
        return False

def test_bot_permissions(chat_id):
    """Test if bot has necessary permissions in the chat"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember", 
                              params={'chat_id': chat_id, 'user_id': BOT_TOKEN.split(':')[0]})
        
        if response.status_code == 200:
            member_info = response.json()['result']
            status = member_info['status']
            permissions = member_info.get('permissions', {})
            
            print(f"🔐 Bot Permissions in Chat:")
            print(f"   Status: {status}")
            print(f"   Can Send Messages: {permissions.get('can_send_messages', False)}")
            print(f"   Can Send Media Messages: {permissions.get('can_send_media_messages', False)}")
            print(f"   Can Send Other Messages: {permissions.get('can_send_other_messages', False)}")
            
            return permissions.get('can_send_messages', False)
        else:
            print(f"❌ Failed to get bot permissions: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking bot permissions: {e}")
        return False

def simulate_new_member_event(chat_id, user_name="Test User"):
    """Simulate the new member event (this is just for testing the message format)"""
    print(f"\n🧪 Simulating new member event...")
    print(f"   Chat ID: {chat_id}")
    print(f"   User Name: {user_name}")
    
    return test_welcome_message(chat_id, user_name)

def main():
    """Main test function"""
    print("🧪 SAFE GUARD BOT - Welcome Message Test")
    print("=" * 50)
    
    # Check bot info
    bot_info = get_bot_info()
    if not bot_info:
        print("❌ Cannot proceed without bot info")
        return
    
    print()
    
    # Check if test chat ID is provided
    if not TEST_CHAT_ID:
        print("⚠️  No TEST_CHAT_ID provided in .env file")
        print("💡 Add TEST_CHAT_ID=your_group_chat_id to your .env file")
        print("📝 You can get your group chat ID by:")
        print("   1. Adding @userinfobot to your group")
        print("   2. Sending /start in the group")
        print("   3. Copying the 'Chat ID' number")
        return
    
    # Check chat info
    chat_info = get_chat_info(TEST_CHAT_ID)
    if not chat_info:
        print("❌ Cannot proceed without chat info")
        return
    
    print()
    
    # Check bot permissions
    has_permissions = test_bot_permissions(TEST_CHAT_ID)
    if not has_permissions:
        print("❌ Bot doesn't have permission to send messages in this chat")
        print("💡 Make sure the bot is added to the group and has 'Send Messages' permission")
        return
    
    print()
    
    # Test welcome message
    success = simulate_new_member_event(TEST_CHAT_ID, "Test User")
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("📱 Check your group to see the welcome message")
        print("🔗 The button should open your web app")
    else:
        print("\n❌ Test failed!")
        print("🔍 Check the error messages above")

if __name__ == "__main__":
    main() 