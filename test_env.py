#!/usr/bin/env python3
"""
Test script to check environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'default_token')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'default_url')
LOCAL_DEV = os.getenv('LOCAL_DEV', 'false').lower() == 'true'

print("🔧 Environment Variable Test")
print("=" * 40)
print(f"TELEGRAM_BOT_TOKEN: {BOT_TOKEN[:10]}..." if BOT_TOKEN != 'default_token' else "TELEGRAM_BOT_TOKEN: NOT SET")
print(f"WEBAPP_URL: {WEBAPP_URL}")
print(f"LOCAL_DEV: {LOCAL_DEV}")
print(f"LOCAL_DEV (raw): '{os.getenv('LOCAL_DEV', 'NOT_SET')}'")
print("=" * 40)

# Test different values
print("\n🧪 Testing different LOCAL_DEV values:")
test_values = ['true', 'True', 'TRUE', 'false', 'False', 'FALSE', 'not_set']

for value in test_values:
    os.environ['LOCAL_DEV'] = value
    result = os.getenv('LOCAL_DEV', 'false').lower() == 'true'
    print(f"  LOCAL_DEV='{value}' -> {result}")

print("\n✅ Test complete!") 