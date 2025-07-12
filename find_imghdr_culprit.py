#!/usr/bin/env python3
"""
Find imghdr Culprit Script

This script helps identify what's causing the imghdr import error
even after removing all telegram packages.
"""

import sys
import os
import subprocess

def check_python_path():
    """Check Python path and find where imghdr might be coming from"""
    print("🐍 Python Environment Info:")
    print(f"   Python executable: {sys.executable}")
    print(f"   Python version: {sys.version}")
    print(f"   Python path:")
    for path in sys.path:
        print(f"     - {path}")
    print()

def check_imghdr_import():
    """Try to import imghdr and see what happens"""
    print("🔍 Testing imghdr import...")
    try:
        import imghdr
        print(f"❌ imghdr IS available at: {imghdr.__file__}")
        return True
    except ImportError:
        print("✅ imghdr is NOT available (this is correct for Python 3.13)")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing imghdr: {e}")
        return False

def check_telegram_import():
    """Check what happens when importing telegram"""
    print("🔍 Testing telegram import...")
    try:
        import telegram
        print(f"❌ telegram module found at: {telegram.__file__}")
        
        # Check what's inside the telegram module
        print("📦 Contents of telegram module:")
        for item in dir(telegram):
            if not item.startswith('_'):
                print(f"   - {item}")
        
        return True
    except ImportError as e:
        print(f"✅ telegram module not found: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing telegram: {e}")
        return False

def check_site_packages():
    """Check site-packages for telegram-related files"""
    print("📁 Checking site-packages for telegram files...")
    
    # Get site-packages location
    try:
        import site
        site_packages = site.getsitepackages()
        user_site = site.getusersitepackages()
        
        print(f"   System site-packages: {site_packages}")
        print(f"   User site-packages: {user_site}")
        
        # Check for telegram directories
        all_paths = site_packages + [user_site]
        telegram_dirs = []
        
        for path in all_paths:
            if os.path.exists(path):
                for item in os.listdir(path):
                    if 'telegram' in item.lower():
                        full_path = os.path.join(path, item)
                        telegram_dirs.append(full_path)
                        print(f"   Found: {full_path}")
        
        if not telegram_dirs:
            print("   No telegram directories found in site-packages")
        
        return telegram_dirs
        
    except Exception as e:
        print(f"❌ Error checking site-packages: {e}")
        return []

def check_pip_list():
    """Check what packages are installed"""
    print("📦 Checking installed packages...")
    try:
        result = subprocess.run("pip list", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            telegram_packages = []
            for line in lines:
                if 'telegram' in line.lower():
                    telegram_packages.append(line.strip())
            
            if telegram_packages:
                print("   Found telegram packages:")
                for pkg in telegram_packages:
                    print(f"     - {pkg}")
            else:
                print("   No telegram packages found in pip list")
            
            return telegram_packages
        else:
            print(f"❌ Error running pip list: {result.stderr}")
            return []
    except Exception as e:
        print(f"❌ Error checking pip list: {e}")
        return []

def check_importlib():
    """Use importlib to find where modules are coming from"""
    print("🔍 Using importlib to trace imports...")
    try:
        import importlib.util
        
        # Try to find telegram module
        spec = importlib.util.find_spec('telegram')
        if spec:
            print(f"❌ telegram module found at: {spec.origin}")
            print(f"   Loader: {spec.loader}")
            print(f"   Submodule search locations: {spec.submodule_search_locations}")
        else:
            print("✅ telegram module not found by importlib")
        
        # Try to find imghdr module
        spec = importlib.util.find_spec('imghdr')
        if spec:
            print(f"❌ imghdr module found at: {spec.origin}")
        else:
            print("✅ imghdr module not found by importlib")
            
    except Exception as e:
        print(f"❌ Error using importlib: {e}")

def main():
    """Main diagnostic function"""
    print("🔍 imghdr Culprit Finder")
    print("=" * 50)
    
    # Check Python environment
    check_python_path()
    
    # Check for imghdr
    imghdr_available = check_imghdr_import()
    
    # Check for telegram
    telegram_available = check_telegram_import()
    
    # Check site-packages
    telegram_dirs = check_site_packages()
    
    # Check pip list
    telegram_packages = check_pip_list()
    
    # Use importlib
    check_importlib()
    
    print()
    print("📋 Summary:")
    print(f"   imghdr available: {imghdr_available}")
    print(f"   telegram available: {telegram_available}")
    print(f"   telegram directories: {len(telegram_dirs)}")
    print(f"   telegram packages: {len(telegram_packages)}")
    
    if imghdr_available:
        print()
        print("❌ PROBLEM: imghdr is available but shouldn't be in Python 3.13")
        print("💡 This suggests you might be using Python 3.12 or earlier")
        print("💡 Or there's a conflicting package that provides imghdr")
    
    if telegram_available:
        print()
        print("❌ PROBLEM: telegram module is still available")
        print("💡 This means the uninstall didn't work completely")
    
    print()
    print("🔧 Next Steps:")
    if imghdr_available or telegram_available:
        print("1. Check if you're using the correct Python version")
        print("2. Try using a virtual environment")
        print("3. Check for system-wide packages")
    else:
        print("✅ Environment looks clean!")
        print("💡 Try installing python-telegram-bot==13.15 again")

if __name__ == "__main__":
    main() 