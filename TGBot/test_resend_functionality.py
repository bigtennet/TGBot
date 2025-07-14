#!/usr/bin/env python3
"""
Test script for resend functionality
"""

import requests
import json
import time

def test_resend_functionality():
    """Test the resend code functionality"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Resend Functionality")
    print("=" * 40)
    
    # Step 1: Test initial login
    print("1. Testing initial login...")
    login_data = {
        "phone_number": "1234567890"  # Test phone number
    }
    
    try:
        response = requests.post(
            f"{base_url}/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Initial login successful")
                print(f"   Message: {data.get('message')}")
            else:
                print("❌ Initial login failed")
                print(f"   Error: {data.get('error')}")
                return False
        else:
            print(f"❌ Login request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login request error: {e}")
        return False
    
    # Step 2: Test resend functionality
    print("\n2. Testing resend functionality...")
    resend_data = {
        "phone_number": "resend"
    }
    
    try:
        response = requests.post(
            f"{base_url}/login",
            json=resend_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Resend successful")
                print(f"   Message: {data.get('message')}")
                print(f"   Phone: {data.get('phone_number')}")
            else:
                print("❌ Resend failed")
                print(f"   Error: {data.get('error')}")
                return False
        else:
            print(f"❌ Resend request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Resend request error: {e}")
        return False
    
    # Step 3: Test resend without session
    print("\n3. Testing resend without session...")
    
    # Create a new session
    session = requests.Session()
    
    try:
        response = session.post(
            f"{base_url}/login",
            json=resend_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            data = response.json()
            if "No phone number found" in data.get('error', ''):
                print("✅ Correctly rejected resend without phone number")
            else:
                print(f"❌ Unexpected error: {data.get('error')}")
                return False
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Session test error: {e}")
        return False
    
    print("\n🎉 All tests passed!")
    return True

def test_verify_page_resend():
    """Test the resend functionality from the verify page perspective"""
    
    print("\n🌐 Testing Verify Page Resend")
    print("=" * 40)
    
    # This would require a browser automation tool like Selenium
    # For now, we'll just test the API endpoint
    
    print("✅ API endpoint tests completed")
    print("💡 To test the full UI flow, use a browser and:")
    print("   1. Go to /login and enter a phone number")
    print("   2. Go to /verify page")
    print("   3. Click 'Resend code' button")
    print("   4. Check if new code is sent")

if __name__ == "__main__":
    print("🚀 Starting Resend Functionality Tests")
    print("Make sure your Flask app is running on http://localhost:5000")
    print()
    
    success = test_resend_functionality()
    
    if success:
        test_verify_page_resend()
        print("\n✅ All functionality tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the errors above.") 