#!/usr/bin/env python3
"""
MongoDB Setup for TGBot
Helps users set up MongoDB for the TGBot system
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_mongodb_installed():
    """Check if MongoDB is installed"""
    try:
        result = subprocess.run(['mongod', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ MongoDB is installed")
            print(f"📋 Version: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ MongoDB is not installed or not in PATH")
    return False

def check_mongodb_running():
    """Check if MongoDB service is running"""
    try:
        # Try to connect to MongoDB
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", 
                                   serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        client.close()
        print("✅ MongoDB service is running")
        return True
    except Exception as e:
        print(f"❌ MongoDB service is not running: {e}")
        return False

def install_mongodb_instructions():
    """Show instructions for installing MongoDB"""
    system = platform.system().lower()
    
    print("\n📦 MongoDB Installation Instructions:")
    print("=" * 50)
    
    if system == "windows":
        print("🪟 Windows:")
        print("1. Download MongoDB Community Server from:")
        print("   https://www.mongodb.com/try/download/community")
        print("2. Run the installer and follow the setup wizard")
        print("3. Make sure to install MongoDB as a service")
        print("4. Add MongoDB bin directory to your PATH")
        
    elif system == "darwin":  # macOS
        print("🍎 macOS:")
        print("1. Install using Homebrew:")
        print("   brew tap mongodb/brew")
        print("   brew install mongodb-community")
        print("2. Start MongoDB service:")
        print("   brew services start mongodb/brew/mongodb-community")
        
    elif system == "linux":
        print("🐧 Linux (Ubuntu/Debian):")
        print("1. Import MongoDB public GPG key:")
        print("   wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -")
        print("2. Add MongoDB repository:")
        print("   echo 'deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list")
        print("3. Update package database:")
        print("   sudo apt-get update")
        print("4. Install MongoDB:")
        print("   sudo apt-get install -y mongodb-org")
        print("5. Start MongoDB service:")
        print("   sudo systemctl start mongod")
        print("6. Enable MongoDB to start on boot:")
        print("   sudo systemctl enable mongod")
    
    print("\n💡 Alternative: Use MongoDB Atlas (cloud service)")
    print("1. Go to https://www.mongodb.com/atlas")
    print("2. Create a free account")
    print("3. Create a new cluster")
    print("4. Get your connection string")
    print("5. Update your .env file with the connection string")

def setup_env_file():
    """Set up environment file with MongoDB configuration"""
    env_file = Path(".env")
    env_template = Path("env_template.txt")
    
    if not env_file.exists():
        if env_template.exists():
            print("📝 Creating .env file from template...")
            with open(env_template, 'r') as f:
                template_content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(template_content)
            
            print("✅ .env file created from template")
            print("📝 Please edit .env file with your MongoDB connection details")
        else:
            print("❌ env_template.txt not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def test_mongodb_connection():
    """Test MongoDB connection with current settings"""
    print("\n🔌 Testing MongoDB Connection...")
    
    try:
        from utils.mongodb_manager import mongodb_manager
        
        if mongodb_manager.is_connected():
            print("✅ MongoDB connection successful!")
            
            # Get database stats
            stats = mongodb_manager.get_database_stats()
            print(f"📊 Database: {stats.get('database', 'N/A')}")
            print(f"📋 Credentials: {stats.get('collections', {}).get('credentials', 0)}")
            print(f"📦 Sessions: {stats.get('collections', {}).get('sessions', 0)}")
            
            return True
        else:
            print("❌ MongoDB connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MongoDB connection: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 MongoDB Setup for TGBot")
    print("=" * 50)
    
    # Check if MongoDB is installed
    mongodb_installed = check_mongodb_installed()
    
    # Check if MongoDB is running
    mongodb_running = check_mongodb_running()
    
    # Set up environment file
    env_setup = setup_env_file()
    
    if not mongodb_installed:
        install_mongodb_instructions()
        return
    
    if not mongodb_running:
        print("\n🚀 Starting MongoDB...")
        system = platform.system().lower()
        
        if system == "windows":
            print("💡 On Windows, start MongoDB service from Services or run:")
            print("   net start MongoDB")
        elif system == "darwin":
            print("💡 On macOS, start MongoDB with:")
            print("   brew services start mongodb/brew/mongodb-community")
        elif system == "linux":
            print("💡 On Linux, start MongoDB with:")
            print("   sudo systemctl start mongod")
        
        print("\n⏳ Please start MongoDB and run this script again")
        return
    
    # Test connection
    if test_mongodb_connection():
        print("\n🎉 MongoDB setup is complete!")
        print("✅ You can now use TGBot with MongoDB storage")
        
        # Run integration test
        print("\n🧪 Running integration test...")
        try:
            subprocess.run([sys.executable, "test_mongodb_integration.py"], 
                         check=True, timeout=30)
        except subprocess.TimeoutExpired:
            print("⚠️ Integration test timed out")
        except subprocess.CalledProcessError:
            print("⚠️ Integration test failed")
        except FileNotFoundError:
            print("⚠️ Integration test file not found")
    else:
        print("\n❌ MongoDB setup incomplete")
        print("💡 Please check your MongoDB configuration and try again")

if __name__ == "__main__":
    main() 