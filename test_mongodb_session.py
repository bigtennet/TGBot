#!/usr/bin/env python3
"""
Test script to verify MongoDB session storage functionality
"""

import os
import sys
import time
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.mongo_session_manager import MongoSessionManager

def test_mongodb_session():
    """Test MongoDB session storage functionality"""
    print("🧪 Testing MongoDB Session Storage")
    print("=" * 50)
    
    # Create session manager
    session_manager = MongoSessionManager()
    
    # Test 1: Connection
    print("1. Testing MongoDB connection...")
    if session_manager.connected:
        print("✅ MongoDB connection successful")
    else:
        print("❌ MongoDB connection failed")
        return False
    
    # Test 2: Store session
    print("\n2. Testing session storage...")
    test_session_id = f"test_session_{int(time.time())}"
    test_session_data = {
        'phone_number': '+1234567890',
        'phone_code_hash': 'test_hash_123',
        'client': {'test': 'data'},
        'created_at': time.time()
    }
    
    success = session_manager.store_session(test_session_id, test_session_data)
    if success:
        print(f"✅ Session stored successfully: {test_session_id}")
    else:
        print("❌ Failed to store session")
        return False
    
    # Test 3: Retrieve session
    print("\n3. Testing session retrieval...")
    retrieved_data = session_manager.get_session(test_session_id)
    if retrieved_data:
        print(f"✅ Session retrieved successfully")
        print(f"   Phone: {retrieved_data.get('phone_number')}")
        print(f"   Hash: {retrieved_data.get('phone_code_hash')}")
    else:
        print("❌ Failed to retrieve session")
        return False
    
    # Test 4: Session count
    print("\n4. Testing session count...")
    count = session_manager.get_session_count()
    print(f"✅ Active sessions: {count}")
    
    # Test 5: Delete session
    print("\n5. Testing session deletion...")
    deleted = session_manager.delete_session(test_session_id)
    if deleted:
        print("✅ Session deleted successfully")
    else:
        print("❌ Failed to delete session")
    
    # Test 6: Verify deletion
    print("\n6. Verifying session deletion...")
    retrieved_after_delete = session_manager.get_session(test_session_id)
    if retrieved_after_delete is None:
        print("✅ Session properly deleted")
    else:
        print("❌ Session still exists after deletion")
        return False
    
    # Test 7: Cleanup
    print("\n7. Testing cleanup...")
    cleaned_count = session_manager.cleanup_expired_sessions()
    print(f"✅ Cleaned up {cleaned_count} expired sessions")
    
    # Test 8: Close connection
    print("\n8. Testing connection closure...")
    session_manager.close()
    print("✅ MongoDB connection closed")
    
    print("\n" + "=" * 50)
    print("🎉 All MongoDB session tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_mongodb_session()
        if success:
            print("\n✅ MongoDB integration is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ MongoDB integration test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 