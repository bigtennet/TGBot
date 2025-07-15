#!/usr/bin/env python3
"""
Script to manually send welcome messages to Telegram channels
"""

from bot_http import HTTPTelegramBot

def main():
    bot = HTTPTelegramBot()
    
    print("📢 Channel Welcome Message Sender")
    print("=" * 40)
    
    # Get channel ID from user
    channel_id = input("Enter the channel ID (e.g., -1001234567890): ").strip()
    
    if not channel_id:
        print("❌ No channel ID provided")
        return
    
    try:
        # Convert to integer
        channel_id = int(channel_id)
        
        print(f"📤 Sending welcome message to channel {channel_id}...")
        
        # Send the welcome message
        success = bot.send_channel_welcome_message(channel_id)
        
        if success:
            print("✅ Welcome message sent successfully!")
        else:
            print("❌ Failed to send welcome message")
            
    except ValueError:
        print("❌ Invalid channel ID. Please enter a valid number.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 