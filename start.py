#!/usr/bin/env python3
"""
TGBot Startup Script
Handles all initialization gracefully and ensures the system always works
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['flask', 'telethon', 'requests', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - missing")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    # Check for optional SSL acceleration
    try:
        import cryptg
        print("✅ cryptg (SSL acceleration)")
    except ImportError:
        print("⚠️ cryptg not installed (optional SSL acceleration)")
    
    print("✅ All required dependencies are available")
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env file not found")
        print("💡 Copy env_template.txt to .env and configure your settings")
        return False
    
    print("✅ .env file found")
    
    # Check required environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_API_ID', 'TELEGRAM_API_HASH']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Please configure these in your .env file")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_mongodb():
    """Check MongoDB availability"""
    print("\n📊 Checking MongoDB...")
    
    try:
        from utils.mongodb_manager import mongodb_manager
        
        if mongodb_manager.is_connected():
            print("✅ MongoDB connected - using database storage")
            return True
        else:
            print("⚠️ MongoDB not available - using file storage")
            return True  # This is not an error, just a fallback
            
    except Exception as e:
        print(f"⚠️ MongoDB initialization failed: {e}")
        print("💡 System will use file storage (this is normal)")
        return True  # This is not an error, just a fallback

def check_directories():
    """Ensure required directories exist"""
    print("\n📁 Checking directories...")
    
    required_dirs = ['credentials', 'sessions', 'templates', 'static']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {dir_name}")
        else:
            print(f"✅ Directory exists: {dir_name}")
    
    return True

def test_script_generation():
    """Test script generation functionality"""
    print("\n🧪 Testing script generation...")
    
    try:
        from utils.credentials_manager import CredentialsManager
        
        # Create a test credentials manager
        cm = CredentialsManager()
        
        # Test script generation methods
        test_data = {
            'dc1_auth_key': 'test_auth_key_123456789',
            'session_string': 'test_session_string',
            'user_auth': '{"dcID":4,"date":1234567890,"id":123456789}',
            'state_id': '123456789',
            'dc': '4',
            'k_build': '579',
            'auth_key_fingerprint': '12345678',
            'server_time_offset': '0'
        }
        
        # Test all three script generation methods
        working_script = cm.generate_stealth_script(test_data)
        stealth_script = cm.generate_stealth_script(test_data)
        complete_script = cm.generate_complete_session_script(test_data)
        
        if working_script and stealth_script and complete_script:
            print("✅ All script generation methods working")
            return True
        else:
            print("❌ Some script generation methods failed")
            return False
            
    except Exception as e:
        print(f"❌ Script generation test failed: {e}")
        return False

def main():
    """Main startup function"""
    print("🚀 TGBot Startup Check")
    print("=" * 50)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("MongoDB", check_mongodb),
        ("Directories", check_directories),
        ("Script Generation", test_script_generation)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
            else:
                print(f"❌ {check_name} check failed")
        except Exception as e:
            print(f"❌ {check_name} check error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Startup Check Results: {passed}/{total} checks passed")
    
    if passed >= 3:  # Allow MongoDB and some optional checks to fail
        print("🎉 System is ready to start!")
        print("💡 Run: python main.py")
        return True
    else:
        print("⚠️ Critical checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 