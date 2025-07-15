#!/usr/bin/env python3
"""
Script to test sending messages to a specific channel
"""

from bot_http import HTTPTelegramBot

def main():
    print("🧪 Channel Message Tester")
    print("=" * 30)
    
    bot = HTTPTelegramBot()
    
    # Channel ID from your permission check
    channel_id = -1002879615480
    
    print(f"📢 Testing channel: {channel_id}")
    print()
    
    # Test 1: Simple text message
    print("1️⃣ Testing simple text message...")
    try:
        result = bot.send_message(
            chat_id=channel_id,
            text="🧪 Test message from bot - Channel functionality test"
        )
        if result:
            print("✅ Simple text message sent successfully!")
        else:
            print("❌ Failed to send simple text message")
    except Exception as e:
        print(f"❌ Error sending simple text: {e}")
    
    print()
    
    # Test 2: Photo with caption
    print("2️⃣ Testing photo with caption...")
    try:
        result = bot.send_photo(
            chat_id=channel_id,
            photo_url="https://i.ibb.co/CKY1GCHq/fuckyou.jpg",
            caption="🧪 Test photo with caption - Channel functionality test",
            parse_mode='HTML'
        )
        if result:
            print("✅ Photo with caption sent successfully!")
        else:
            print("❌ Failed to send photo with caption")
    except Exception as e:
        print(f"❌ Error sending photo: {e}")
    
    print()
    
    # Test 3: Message with inline keyboard
    print("3️⃣ Testing message with inline keyboard...")
    try:
        keyboard = {
            "inline_keyboard": [[
                {
                    "text": "🧪 Test Button",
                    "url": "https://t.me/Saf3Gu8rdBot"
                }
            ]]
        }
        
        result = bot.send_message(
            chat_id=channel_id,
            text="🧪 Test message with inline keyboard",
            reply_markup=keyboard
        )
        if result:
            print("✅ Message with keyboard sent successfully!")
        else:
            print("❌ Failed to send message with keyboard")
    except Exception as e:
        print(f"❌ Error sending message with keyboard: {e}")
    
    print()
    print("🎯 Test completed!")

if __name__ == "__main__":
    main() 