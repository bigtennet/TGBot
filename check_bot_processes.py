#!/usr/bin/env python3
"""
Check for Running Bot Processes

This script helps identify if multiple bot instances are running.
"""

import os
import subprocess
import psutil
import sys

def find_python_processes():
    """Find all Python processes that might be running the bot"""
    bot_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if it's a Python process
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline:
                    # Check if it's running bot_http.py or similar
                    cmd_str = ' '.join(cmdline)
                    if any(keyword in cmd_str.lower() for keyword in ['bot_http', 'bot_runner', 'main.py']):
                        bot_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmd_str,
                            'create_time': proc.create_time()
                        })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return bot_processes

def check_telegram_api_conflict():
    """Check if there's a Telegram API conflict by testing getUpdates"""
    import requests
    from dotenv import load_dotenv
    
    load_dotenv()
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '7977799957:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
    
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates", 
                              params={'limit': 1, 'timeout': 1})
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                return False, "No conflict detected"
            else:
                error_desc = result.get('description', '')
                if 'Conflict' in error_desc:
                    return True, f"Conflict detected: {error_desc}"
                else:
                    return False, f"Other error: {error_desc}"
        else:
            return False, f"HTTP error: {response.status_code}"
    except Exception as e:
        return False, f"Request error: {e}"

def main():
    """Main function to check bot processes"""
    print("🔍 Bot Process Checker")
    print("=" * 40)
    
    # Check for running bot processes
    print("\n1. Checking for running bot processes...")
    bot_processes = find_python_processes()
    
    if bot_processes:
        print(f"⚠️  Found {len(bot_processes)} potential bot processes:")
        for i, proc in enumerate(bot_processes, 1):
            print(f"   {i}. PID: {proc['pid']}")
            print(f"      Command: {proc['cmdline']}")
            print(f"      Started: {proc['create_time']}")
            print()
    else:
        print("✅ No bot processes found running")
    
    # Check for Telegram API conflicts
    print("2. Checking for Telegram API conflicts...")
    has_conflict, message = check_telegram_api_conflict()
    
    if has_conflict:
        print(f"❌ {message}")
        print("\n🔧 To fix this:")
        print("   1. Stop all bot processes above")
        print("   2. Run: python fix_bot_conflict.py")
        print("   3. Wait 1-2 minutes")
        print("   4. Start only ONE bot instance")
    else:
        print(f"✅ {message}")
    
    # Summary
    print("\n📋 Summary:")
    if bot_processes:
        print(f"   - {len(bot_processes)} bot processes running")
        print("   - Consider stopping extra instances")
    else:
        print("   - No bot processes found")
    
    if has_conflict:
        print("   - Telegram API conflict detected")
        print("   - Run fix_bot_conflict.py to resolve")
    else:
        print("   - No Telegram API conflicts")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if len(bot_processes) > 1:
        print("   - Stop all but one bot instance")
        print("   - Use 'taskkill /PID <pid>' on Windows")
        print("   - Use 'kill <pid>' on Linux/Mac")
    elif len(bot_processes) == 1:
        print("   - One bot instance running (good)")
    else:
        print("   - No bot instances running")
        print("   - Start your bot with: python bot_http.py")
    
    if has_conflict:
        print("   - Run: python fix_bot_conflict.py")
        print("   - Wait 1-2 minutes before starting bot")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Check interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during check: {e}")
        print("Try running: pip install psutil") 