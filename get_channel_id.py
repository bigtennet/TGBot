#!/usr/bin/env python3
"""
Script to get Telegram channel ID using the bot
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')

def get_bot_info():
    """Get bot information"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"❌ Error getting bot info: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("📢 Channel ID Finder")
    print("=" * 30)
    
    # Get bot info
    bot_info = get_bot_info()
    if not bot_info:
        print("❌ Could not get bot information")
        return
    
    bot_username = bot_info['username']
    
    print(f"🤖 Bot: @{bot_username}")
    print()
    print("📋 Instructions:")
    print("1. Add your bot as admin to the channel")
    print("2. Post any message in the channel")
    print("3. The bot will detect the channel and show its ID")
    print()
    print("🔍 The bot will automatically detect channel posts and log the channel ID")
    print("💡 Check your bot logs after posting in the channel")
    print()
    print("📝 Alternative: Use @userinfobot in the channel")

if __name__ == "__main__":
    main() 