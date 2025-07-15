#!/usr/bin/env python3
"""
Test script for admin commands functionality
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from utils.user_id_manager import UserIDManager
from config import ADMIN_PASSWORD

def test_user_id_manager():
    """Test the UserIDManager functionality"""
    print("🧪 Testing UserIDManager...")
    
    # Initialize manager
    manager = UserIDManager("test_user_ids.json")
    
    # Test adding user IDs
    print("\n📝 Testing add_user_id...")
    test_ids = ["123456789", "987654321", "555666777"]
    
    for user_id in test_ids:
        success = manager.add_user_id(user_id)
        print(f"   Adding {user_id}: {'✅ Success' if success else '❌ Failed'}")
    
    # Test adding duplicate
    print(f"\n🔄 Testing duplicate add...")
    success = manager.add_user_id("123456789")
    print(f"   Adding duplicate 123456789: {'✅ Success' if success else '❌ Failed (expected)'}")
    
    # Test adding invalid ID
    print(f"\n⚠️ Testing invalid ID...")
    success = manager.add_user_id("invalid_id")
    print(f"   Adding invalid_id: {'✅ Success' if success else '❌ Failed (expected)'}")
    
    # Test getting user IDs
    print(f"\n📋 Testing get_user_ids...")
    user_ids = manager.get_user_ids()
    print(f"   Total user IDs: {len(user_ids)}")
    print(f"   User IDs: {user_ids}")
    
    # Test deleting user ID
    print(f"\n🗑️ Testing delete_user_id...")
    success = manager.delete_user_id("123456789")
    print(f"   Deleting 123456789: {'✅ Success' if success else '❌ Failed'}")
    
    # Test deleting non-existent ID
    success = manager.delete_user_id("999999999")
    print(f"   Deleting non-existent 999999999: {'✅ Success' if success else '❌ Failed (expected)'}")
    
    # Test final state
    print(f"\n📊 Final state...")
    user_ids = manager.get_user_ids()
    print(f"   Total user IDs: {len(user_ids)}")
    print(f"   User IDs: {user_ids}")
    
    # Clean up test file
    try:
        os.remove("test_user_ids.json")
        print(f"\n🧹 Cleaned up test file")
    except:
        pass
    
    print(f"\n✅ UserIDManager test completed!")

def test_admin_password():
    """Test admin password configuration"""
    print(f"\n🔐 Testing admin password configuration...")
    print(f"   ADMIN_PASSWORD from config: {ADMIN_PASSWORD}")
    
    if ADMIN_PASSWORD == "admin_password_change_this":
        print("   ⚠️ Warning: Using default admin password!")
    else:
        print("   ✅ Custom admin password configured")

if __name__ == "__main__":
    print("🤖 Admin Commands Test Suite")
    print("=" * 40)
    
    test_admin_password()
    test_user_id_manager()
    
    print(f"\n📋 Available Commands:")
    print(f"   /add_userId - Add a user ID to the list")
    print(f"   /del_userId - Delete a user ID from the list")
    print(f"   /userId - List all user IDs")
    print(f"   /cancel - Cancel current operation")
    
    print(f"\n🔐 Admin Password: {ADMIN_PASSWORD}")
    print(f"💡 Make sure to set ADMIN_PASSWORD in your .env file for security!") 