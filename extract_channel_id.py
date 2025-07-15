#!/usr/bin/env python3
"""
Script to extract channel ID from Telegram URLs
"""

import re

def extract_channel_id_from_url(url):
    """Extract channel ID from Telegram URL"""
    patterns = [
        r'https://web\.telegram\.org/k/#(-?\d+)',  # Web URL
        r'https://t\.me/([^/]+)',  # t.me URL
        r'@([a-zA-Z0-9_]+)',  # Username
        r'(-?\d+)',  # Just the number
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def main():
    print("🔍 Channel ID Extractor")
    print("=" * 30)
    print()
    print("📋 Supported formats:")
    print("• https://web.telegram.org/k/#-1001234567890")
    print("• https://t.me/channelname")
    print("• @channelname")
    print("• -1001234567890")
    print()
    
    while True:
        url = input("Enter Telegram URL or channel ID: ").strip()
        
        if not url:
            print("❌ No input provided")
            continue
        
        if url.lower() == 'quit':
            break
        
        channel_id = extract_channel_id_from_url(url)
        
        if channel_id:
            print(f"✅ Channel ID: {channel_id}")
            
            # Determine if it's a channel or group
            if channel_id.startswith('-100'):
                print("📢 This is a channel ID")
            elif channel_id.startswith('-'):
                print("👥 This is a group ID")
            else:
                print("❓ Could be a user ID or username")
        else:
            print("❌ Could not extract channel ID")
        
        print()

if __name__ == "__main__":
    main() 