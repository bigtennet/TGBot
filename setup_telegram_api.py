#!/usr/bin/env python3
"""
Telegram API Setup Script
This script helps you set up your Telegram API credentials for the Safeguard Bot.
"""

import os
import sys

def main():
    print("🔧 Telegram API Setup for Safeguard Bot")
    print("=" * 50)
    print()
    print("To use phone number authentication, you need Telegram API credentials.")
    print("Follow these steps:")
    print()
    print("1. Go to https://my.telegram.org")
    print("2. Log in with your phone number")
    print("3. Click on 'API development tools'")
    print("4. Create a new application (if you don't have one)")
    print("5. Note down your 'api_id' and 'api_hash'")
    print()
    
    # Check if .env file exists
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ Found existing {env_file} file")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'your_telegram_api_id_here' in content:
                print("⚠️  API credentials not configured yet")
            else:
                print("✅ API credentials appear to be configured")
    else:
        print(f"❌ {env_file} file not found")
    
    print()
    print("Current environment variables:")
    api_id = os.environ.get('TELEGRAM_API_ID')
    api_hash = os.environ.get('TELEGRAM_API_HASH')
    
    if api_id and api_id != 'your_telegram_api_id_here':
        print(f"✅ TELEGRAM_API_ID: {api_id[:4]}...{api_id[-4:] if len(api_id) > 8 else '***'}")
    else:
        print("❌ TELEGRAM_API_ID: Not set")
    
    if api_hash and api_hash != 'your_telegram_api_hash_here':
        print(f"✅ TELEGRAM_API_HASH: {api_hash[:8]}...{api_hash[-8:] if len(api_hash) > 16 else '***'}")
    else:
        print("❌ TELEGRAM_API_HASH: Not set")
    
    print()
    print("To set up your credentials:")
    print("1. Create a .env file in the project root")
    print("2. Add these lines to the .env file:")
    print("   TELEGRAM_API_ID=your_actual_api_id")
    print("   TELEGRAM_API_HASH=your_actual_api_hash")
    print()
    print("Example .env file content:")
    print("-" * 30)
    print("TELEGRAM_BOT_TOKEN=8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k")
    print("BOT_USERNAME=safeguard_bot")
    print("TELEGRAM_API_ID=12345678")
    print("TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890")
    print("SECRET_KEY=your-secret-key-here")
    print("-" * 30)
    print()
    print("After setting up the .env file, restart the Flask app.")
    print()
    
    # Test import
    try:
        from utils.tg.auth import telegram_auth
        print("✅ Telegram auth module imported successfully")
        
        if telegram_auth.api_id and telegram_auth.api_id != 'your_api_id':
            print("✅ API credentials loaded from config")
        else:
            print("❌ API credentials not properly configured")
            
    except ImportError as e:
        print(f"❌ Error importing auth module: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 