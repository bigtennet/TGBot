#!/usr/bin/env python3
"""
Script to resolve channel usernames to numeric IDs using Telegram API
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')

def get_chat_info(chat_id_or_username):
    """Get chat information from Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    data = {
        'chat_id': chat_id_or_username
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("🔍 Channel ID Resolver")
    print("=" * 30)
    print()
    print("📋 This script resolves usernames to numeric channel IDs")
    print("💡 Make sure your bot is added to the channel as admin")
    print()
    
    while True:
        username = input("Enter channel username (without @) or 'quit': ").strip()
        
        if not username:
            print("❌ No username provided")
            continue
        
        if username.lower() == 'quit':
            break
        
        # Remove @ if present
        if username.startswith('@'):
            username = username[1:]
        
        print(f"🔍 Resolving @{username}...")
        
        # Try to get chat info
        chat_info = get_chat_info(f"@{username}")
        
        if chat_info:
            chat_id = chat_info.get('id')
            chat_type = chat_info.get('type', 'unknown')
            chat_title = chat_info.get('title', 'Unknown')
            chat_username = chat_info.get('username', 'No username')
            
            print(f"✅ Success!")
            print(f"   📝 Title: {chat_title}")
            print(f"   🆔 ID: {chat_id}")
            print(f"   👤 Username: @{chat_username}")
            print(f"   📋 Type: {chat_type}")
            
            # Determine chat type
            if chat_type == 'channel':
                print("📢 This is a channel")
            elif chat_type == 'group':
                print("👥 This is a group")
            elif chat_type == 'supergroup':
                print("👥 This is a supergroup")
            else:
                print(f"❓ Unknown type: {chat_type}")
                
        else:
            print(f"❌ Could not resolve @{username}")
            print("💡 Make sure:")
            print("   • The channel exists")
            print("   • Your bot is added to the channel")
            print("   • Your bot has permission to view the channel")
        
        print()

if __name__ == "__main__":
    main() 