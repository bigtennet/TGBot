#!/usr/bin/env python3
"""
Test script for verification broadcast functionality
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from utils.user_id_manager import UserIDManager
from config import SCRIPT_TARGET_USER_ID

def test_verification_broadcast():
    """Test the verification broadcast functionality"""
    print("🧪 Testing Verification Broadcast...")
    
    # Initialize manager
    manager = UserIDManager("test_user_ids.json")
    
    # Add some test user IDs
    print("\n📝 Adding test user IDs...")
    test_ids = ["123456789", "987654321", "555666777"]
    
    for user_id in test_ids:
        success = manager.add_user_id(user_id)
        print(f"   Adding {user_id}: {'✅ Success' if success else '❌ Failed'}")
    
    # Test getting user IDs
    print(f"\n📋 Current user IDs in list:")
    user_ids = manager.get_user_ids()
    print(f"   Total: {len(user_ids)}")
    print(f"   IDs: {user_ids}")
    
    # Test the broadcast functionality (without actually sending)
    print(f"\n📤 Testing broadcast logic...")
    if user_ids:
        print(f"   Would send verification to {len(user_ids)} user(s)")
        for user_id in user_ids:
            print(f"   - User ID: {user_id}")
    else:
        print("   No user IDs to broadcast to")
    
    # Clean up test file
    try:
        os.remove("test_user_ids.json")
        print(f"\n🧹 Cleaned up test file")
    except:
        pass
    
    print(f"\n✅ Verification broadcast test completed!")

def test_authorization():
    """Test authorization logic"""
    print(f"\n🔐 Testing Authorization...")
    print(f"   SCRIPT_TARGET_USER_ID: {SCRIPT_TARGET_USER_ID}")
    
    if SCRIPT_TARGET_USER_ID:
        print(f"   ✅ SCRIPT_TARGET_USER_ID is configured")
        print(f"   📝 Only user {SCRIPT_TARGET_USER_ID} can:")
        print(f"      - Add user IDs (/add_userId)")
        print(f"      - Delete user IDs (/del_userId)")
        print(f"      - Broadcast verification (/broadcast_verify)")
        print(f"   📝 Anyone can:")
        print(f"      - List user IDs (/userId)")
    else:
        print(f"   ⚠️ SCRIPT_TARGET_USER_ID is not configured")
        print(f"   📝 No one can use admin commands until it's set")

if __name__ == "__main__":
    print("🤖 Verification Broadcast Test Suite")
    print("=" * 50)
    
    test_authorization()
    test_verification_broadcast()
    
    print(f"\n📋 Available Commands:")
    print(f"   /start - Start the bot and get welcome message")
    print(f"   /help - Show all available commands")
    print(f"   /add_userId - Add a user ID to the list (admin only)")
    print(f"   /del_userId - Delete a user ID from the list (admin only)")
    print(f"   /userId - List all user IDs (anyone)")
    print(f"   /broadcast_verify - Manually trigger verification broadcast (admin only)")
    print(f"   /cancel - Cancel current operation")
    
    print(f"\n🔄 Automatic Triggers:")
    print(f"   - When new members join groups")
    print(f"   - When someone types 'verify' in chat")
    
    print(f"\n💡 Make sure to:")
    print(f"   1. Set SCRIPT_TARGET_USER_ID in your .env file")
    print(f"   2. Add user IDs using /add_userId command")
    print(f"   3. Test with /broadcast_verify command") 