#!/usr/bin/env python3
"""
Fix Bot Permissions Script

This script helps diagnose and fix bot permission issues in Telegram groups.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
TEST_CHAT_ID = os.getenv('TEST_CHAT_ID')

def get_bot_info():
    """Get bot information"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"❌ Failed to get bot info: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return None

def get_chat_member(chat_id):
    """Get bot's member status in the chat"""
    try:
        bot_id = BOT_TOKEN.split(':')[0]
        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember",
            params={'chat_id': chat_id, 'user_id': bot_id}
        )
        
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"❌ Failed to get chat member: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting chat member: {e}")
        return None

def get_chat_info(chat_id):
    """Get chat information"""
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getChat",
            params={'chat_id': chat_id}
        )
        
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"❌ Failed to get chat info: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting chat info: {e}")
        return None

def test_message_access(chat_id):
    """Test if bot can send and receive messages"""
    try:
        # Test sending a message
        test_message = "🔧 Bot permission test message"
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": test_message
            }
        )
        
        if response.status_code == 200:
            message_id = response.json()['result']['message_id']
            print(f"✅ Can send messages (Message ID: {message_id})")
            
            # Try to delete the test message
            try:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id
                    }
                )
                print("✅ Can delete messages")
            except:
                print("⚠️  Cannot delete messages (normal for non-admin)")
            
            return True
        else:
            print(f"❌ Cannot send messages: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing message access: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Bot Permission Fixer")
    print("=" * 40)
    
    # Get bot info
    bot_info = get_bot_info()
    if not bot_info:
        print("❌ Cannot get bot info")
        return
    
    print(f"🤖 Bot: @{bot_info['username']} ({bot_info['first_name']})")
    print()
    
    if not TEST_CHAT_ID:
        print("⚠️  No TEST_CHAT_ID provided")
        print("💡 Add TEST_CHAT_ID=your_group_chat_id to your .env file")
        print("📝 Run get_chat_id.py first to find your chat ID")
        return
    
    # Get chat info
    chat_info = get_chat_info(TEST_CHAT_ID)
    if not chat_info:
        print("❌ Cannot get chat info")
        return
    
    print(f"💬 Chat: {chat_info.get('title', 'Private Chat')} (ID: {chat_info['id']})")
    print(f"📝 Type: {chat_info['type']}")
    print()
    
    # Get bot member status
    member_info = get_chat_member(TEST_CHAT_ID)
    if not member_info:
        print("❌ Bot is not a member of this chat")
        print("💡 Add the bot to the group first")
        return
    
    print("🔐 Bot Permissions:")
    print(f"   Status: {member_info['status']}")
    
    if 'permissions' in member_info:
        permissions = member_info['permissions']
        print(f"   Can Send Messages: {permissions.get('can_send_messages', False)}")
        print(f"   Can Send Media Messages: {permissions.get('can_send_media_messages', False)}")
        print(f"   Can Send Other Messages: {permissions.get('can_send_other_messages', False)}")
        print(f"   Can Add Web Page Previews: {permissions.get('can_add_web_page_previews', False)}")
        print(f"   Can Change Info: {permissions.get('can_change_info', False)}")
        print(f"   Can Invite Users: {permissions.get('can_invite_users', False)}")
        print(f"   Can Pin Messages: {permissions.get('can_pin_messages', False)}")
    
    print()
    
    # Test message access
    print("🧪 Testing Message Access...")
    can_send = test_message_access(TEST_CHAT_ID)
    
    print()
    
    # Provide solutions
    print("💡 Solutions for 'has no access to messages' error:")
    print()
    
    if member_info['status'] == 'left':
        print("❌ Bot has left the group")
        print("   Solution: Re-add the bot to the group")
    
    elif member_info['status'] == 'kicked':
        print("❌ Bot was kicked from the group")
        print("   Solution: Re-add the bot to the group")
    
    elif member_info['status'] == 'restricted':
        print("⚠️  Bot is restricted in the group")
        print("   Solution: Ask admin to remove restrictions")
    
    elif member_info['status'] == 'member':
        print("✅ Bot is a member")
        if can_send:
            print("✅ Bot can send messages")
            print("💡 For new member detection, the bot needs to:")
            print("   1. Be a member of the group")
            print("   2. Have permission to read messages")
            print("   3. Be running (python bot_runner.py)")
            print()
            print("🔧 Try these steps:")
            print("   1. Make sure bot is running: python bot_runner.py")
            print("   2. Add a new user to the group")
            print("   3. Check bot logs for new member events")
        else:
            print("❌ Bot cannot send messages")
            print("   Solution: Ask admin to give bot 'Send Messages' permission")
    
    elif member_info['status'] == 'administrator':
        print("✅ Bot is an administrator")
        if can_send:
            print("✅ Bot has full permissions")
            print("💡 Bot should be able to detect new members")
        else:
            print("❌ Bot cannot send messages despite being admin")
            print("   Solution: Check admin permissions")
    
    print()
    print("📋 Quick Fix Checklist:")
    print("   ☐ Bot is added to the group")
    print("   ☐ Bot has 'Send Messages' permission")
    print("   ☐ Bot is running (python bot_runner.py)")
    print("   ☐ Group allows bots to read messages")
    print("   ☐ Test with a new user joining")

if __name__ == "__main__":
    main() 