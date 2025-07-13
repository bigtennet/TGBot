#!/usr/bin/env python3
"""
Fix Telegram Bot Conflict Script

This script helps resolve the "Conflict: terminated by other getUpdates request" error
by clearing webhooks and checking for multiple bot instances.
"""

import os
import requests
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7977799957:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def check_bot_info():
    """Check if bot token is valid and get bot info"""
    try:
        response = requests.get(f"{BASE_URL}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                print(f"✅ Bot info retrieved successfully")
                print(f"   Username: @{bot_info['result']['username']}")
                print(f"   Name: {bot_info['result']['first_name']}")
                print(f"   ID: {bot_info['result']['id']}")
                return True
            else:
                print(f"❌ Bot API error: {bot_info.get('description')}")
                return False
        else:
            print(f"❌ Failed to get bot info: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking bot info: {e}")
        return False

def get_webhook_info():
    """Get current webhook information"""
    try:
        response = requests.get(f"{BASE_URL}/getWebhookInfo")
        if response.status_code == 200:
            webhook_info = response.json()
            if webhook_info.get('ok'):
                result = webhook_info['result']
                print(f"📡 Webhook Info:")
                print(f"   URL: {result.get('url', 'Not set')}")
                print(f"   Has custom certificate: {result.get('has_custom_certificate', False)}")
                print(f"   Pending update count: {result.get('pending_update_count', 0)}")
                print(f"   Last error date: {result.get('last_error_date')}")
                print(f"   Last error message: {result.get('last_error_message')}")
                return result
            else:
                print(f"❌ Failed to get webhook info: {webhook_info.get('description')}")
                return None
        else:
            print(f"❌ Failed to get webhook info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")
        return None

def delete_webhook():
    """Delete webhook to enable polling"""
    try:
        response = requests.get(f"{BASE_URL}/deleteWebhook")
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook deleted successfully")
                return True
            else:
                print(f"❌ Failed to delete webhook: {result.get('description')}")
                return False
        else:
            print(f"❌ Failed to delete webhook: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
        return False

def test_polling():
    """Test if polling works by getting one update"""
    try:
        print("🧪 Testing polling...")
        response = requests.get(f"{BASE_URL}/getUpdates", params={'limit': 1, 'timeout': 1})
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Polling test successful")
                return True
            else:
                error_desc = result.get('description', 'Unknown error')
                if 'Conflict' in error_desc:
                    print("❌ Polling conflict detected - another instance is running")
                else:
                    print(f"❌ Polling test failed: {error_desc}")
                return False
        else:
            print(f"❌ Polling test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing polling: {e}")
        return False

def clear_updates():
    """Clear any pending updates"""
    try:
        print("🧹 Clearing pending updates...")
        response = requests.get(f"{BASE_URL}/getUpdates", params={'offset': -1})
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                update_count = len(result.get('result', []))
                print(f"✅ Cleared {update_count} pending updates")
                return True
            else:
                print(f"❌ Failed to clear updates: {result.get('description')}")
                return False
        else:
            print(f"❌ Failed to clear updates: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error clearing updates: {e}")
        return False

def main():
    """Main function to fix bot conflicts"""
    print("🔧 Telegram Bot Conflict Fixer")
    print("=" * 50)
    
    # Step 1: Check bot info
    print("\n1. Checking bot information...")
    if not check_bot_info():
        print("❌ Cannot proceed - bot token is invalid")
        return False
    
    # Step 2: Get webhook info
    print("\n2. Checking webhook status...")
    webhook_info = get_webhook_info()
    
    # Step 3: Delete webhook if exists
    if webhook_info and webhook_info.get('url'):
        print(f"\n3. Webhook detected at: {webhook_info['url']}")
        print("   Deleting webhook to enable polling...")
        if not delete_webhook():
            print("❌ Failed to delete webhook")
            return False
    else:
        print("\n3. No webhook detected - polling should work")
    
    # Step 4: Clear pending updates
    print("\n4. Clearing any pending updates...")
    clear_updates()
    
    # Step 5: Wait a moment for Telegram to process
    print("\n5. Waiting for Telegram to process changes...")
    time.sleep(3)
    
    # Step 6: Test polling
    print("\n6. Testing polling functionality...")
    if test_polling():
        print("\n🎉 Bot conflict resolved! You can now start your bot.")
        print("\n💡 Next steps:")
        print("   1. Make sure only ONE instance of your bot is running")
        print("   2. If running locally, stop any Render/VPS instances")
        print("   3. If running on Render, stop any local instances")
        print("   4. Start your bot with: python bot_http.py")
        return True
    else:
        print("\n❌ Polling still not working. Possible issues:")
        print("   - Another bot instance is still running")
        print("   - Bot token is invalid")
        print("   - Network connectivity issues")
        print("\n🔍 Troubleshooting:")
        print("   1. Check all terminals/servers for running bot instances")
        print("   2. Kill any existing bot processes")
        print("   3. Wait 1-2 minutes before trying again")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Fix failed. Please check the errors above.")
    else:
        print("\n✅ Fix completed successfully!") 