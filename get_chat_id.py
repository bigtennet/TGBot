#!/usr/bin/env python3
"""
Get Chat ID Helper Script

This script helps you get the chat ID of a group or channel.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')

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

def main():
    """Main function"""
    print("🔍 Chat ID Finder")
    print("=" * 30)
    print("📝 Instructions:")
    print("1. Add your bot to the group/channel")
    print("2. Send a message in the group/channel")
    print("3. Run this script to see the chat ID")
    print()
    
    # Get bot info
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"🤖 Bot: @{bot_info['username']}")
        else:
            print("❌ Failed to get bot info")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print()
    print("📡 Getting recent updates...")
    
    updates = get_updates()
    
    if not updates:
        print("❌ No updates found!")
        print("💡 Make sure:")
        print("   - Bot is added to the group/channel")
        print("   - Someone sent a message in the group/channel")
        print("   - Bot has permission to read messages")
        return
    
    print(f"✅ Found {len(updates)} updates")
    print()
    
    # Extract unique chats
    chats = {}
    for update in updates:
        if 'message' in update:
            message = update['message']
            chat = message['chat']
            chat_id = chat['id']
            
            if chat_id not in chats:
                chats[chat_id] = {
                    'id': chat_id,
                    'type': chat['type'],
                    'title': chat.get('title', 'Private Chat'),
                    'username': chat.get('username', 'No username'),
                    'first_name': chat.get('first_name', ''),
                    'last_name': chat.get('last_name', '')
                }
    
    if not chats:
        print("❌ No chats found in updates")
        return
    
    print("📋 Found Chats:")
    print("-" * 50)
    
    for chat_id, chat_info in chats.items():
        print(f"🆔 Chat ID: {chat_id}")
        print(f"📝 Type: {chat_info['type']}")
        
        if chat_info['type'] == 'private':
            name = f"{chat_info['first_name']} {chat_info['last_name']}".strip()
            print(f"👤 Name: {name}")
        else:
            print(f"📛 Title: {chat_info['title']}")
            if chat_info['username']:
                print(f"🔗 Username: @{chat_info['username']}")
        
        print(f"📋 .env entry: TEST_CHAT_ID={chat_id}")
        print("-" * 50)
    
    print()
    print("💡 Copy the Chat ID you want to use and add it to your .env file:")
    print("   TEST_CHAT_ID=your_chosen_chat_id")

if __name__ == "__main__":
    main() 