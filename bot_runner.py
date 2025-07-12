#!/usr/bin/env python3
"""
Telegram Bot Runner
This script runs the Safeguard bot independently from the Flask web app.
"""

import os
import sys
from utils.tg.bot import TelegramBot

def main():
    """Main function to run the bot"""
    print("🤖 Starting Safeguard Bot...")
    
    # Bot token - you can set this as environment variable or use the default
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
    
    try:
        # Create and run the bot
        bot = TelegramBot(bot_token)
        print(f"✅ Bot initialized with token: {bot_token[:10]}...")
        print("🚀 Bot is now running. Press Ctrl+C to stop.")
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 