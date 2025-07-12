#!/usr/bin/env python3
"""
Debug Bot Updates Script

This script helps debug why the bot isn't detecting new member events.
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
TEST_CHAT_ID = os.getenv('TEST_CHAT_ID')

def get_updates():
    """Get recent updates from the bot"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
        if response.status_code == 200:
            updates = response.json()['result']
            return updates
        else:
            print(f"❌ Failed to get updates: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting updates: {e}")
        return []

def get_webhook_info():
    """Get webhook information"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"❌ Failed to get webhook info: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")
        return None

def delete_webhook():
    """Delete webhook to ensure polling works"""
    try:
        response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        if response.status_code == 200:
            result = response.json()['result']
            print(f"✅ Webhook deleted: {result}")
            return True
        else:
            print(f"❌ Failed to delete webhook: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
        return False

def test_send_message():
    """Test sending a message to verify bot works"""
    if not TEST_CHAT_ID:
        print("⚠️  No TEST_CHAT_ID provided")
        return False
        
    try:
        test_message = f"🔧 Bot debug test - {datetime.now().strftime('%H:%M:%S')}"
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TEST_CHAT_ID,
                "text": test_message
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Test message sent successfully")
            return True
        else:
            print(f"❌ Failed to send test message: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False

def analyze_updates(updates):
    """Analyze the updates to understand what's happening"""
    if not updates:
        print("📭 No updates found")
        return
    
    print(f"📨 Found {len(updates)} updates")
    print()
    
    for i, update in enumerate(updates[-5:], 1):  # Show last 5 updates
        print(f"📋 Update {i}:")
        print(f"   Update ID: {update.get('update_id')}")
        
        if 'message' in update:
            message = update['message']
            chat = message['chat']
            print(f"   Type: Message")
            print(f"   Chat: {chat.get('title', 'Private')} (ID: {chat['id']})")
            print(f"   From: {message.get('from', {}).get('first_name', 'Unknown')}")
            
            if 'new_chat_members' in message:
                print(f"   📥 NEW MEMBERS EVENT DETECTED!")
                for member in message['new_chat_members']:
                    print(f"      - {member.get('first_name', 'Unknown')} (Bot: {member.get('is_bot', False)})")
            elif 'text' in message:
                print(f"   Text: {message['text'][:50]}...")
            else:
                print(f"   Content: {list(message.keys())}")
        
        elif 'my_chat_member' in update:
            print(f"   Type: My Chat Member Update")
            member = update['my_chat_member']
            print(f"   Chat: {member['chat'].get('title', 'Private')} (ID: {member['chat']['id']})")
            print(f"   Status: {member['new_chat_member']['status']}")
        
        elif 'chat_member' in update:
            print(f"   Type: Chat Member Update")
            member = update['chat_member']
            print(f"   Chat: {member['chat'].get('title', 'Private')} (ID: {member['chat']['id']})")
            print(f"   User: {member['new_chat_member'].get('first_name', 'Unknown')}")
            print(f"   Status: {member['new_chat_member']['status']}")
        
        else:
            print(f"   Type: {list(update.keys())}")
        
        print()

def main():
    """Main function"""
    print("🔍 Bot Updates Debugger")
    print("=" * 40)
    
    # Get bot info
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"🤖 Bot: @{bot_info['username']} ({bot_info['first_name']})")
        else:
            print("❌ Cannot get bot info")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print()
    
    # Check webhook status
    print("🔗 Checking webhook status...")
    webhook_info = get_webhook_info()
    if webhook_info:
        if webhook_info.get('url'):
            print(f"⚠️  Webhook is set to: {webhook_info['url']}")
            print("💡 This might interfere with polling. Deleting webhook...")
            delete_webhook()
        else:
            print("✅ No webhook set (good for polling)")
    
    print()
    
    # Test sending a message
    print("🧪 Testing message sending...")
    test_send_message()
    
    print()
    
    # Get and analyze updates
    print("📡 Getting recent updates...")
    updates = get_updates()
    analyze_updates(updates)
    
    print()
    print("💡 Debugging Tips:")
    print("1. Make sure bot is running: python bot_runner.py")
    print("2. Add a new user to the group")
    print("3. Send a message in the group")
    print("4. Run this script again to see new updates")
    print("5. Check if 'NEW MEMBERS EVENT DETECTED!' appears")
    
    if TEST_CHAT_ID:
        print()
        print(f"🎯 Test Group ID: {TEST_CHAT_ID}")
        print("📝 Try adding a new user to this group and run the script again")

if __name__ == "__main__":
    main() 