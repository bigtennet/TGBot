#!/usr/bin/env python3
"""
Aggressive Telegram Dependencies Fix

This script aggressively removes ALL telegram-related packages and reinstalls
only the correct version for Python 3.13 compatibility.
"""

import subprocess
import sys
import os
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def find_telegram_packages():
    """Find all installed telegram-related packages"""
    try:
        result = subprocess.run("pip list", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            telegram_packages = []
            for line in lines:
                if 'telegram' in line.lower():
                    package_name = line.split()[0]
                    telegram_packages.append(package_name)
            return telegram_packages
        return []
    except:
        return []

def main():
    """Main function to aggressively fix Telegram dependencies"""
    print("🔧 Aggressive Telegram Dependencies Fixer")
    print("=" * 60)
    print("This script will completely remove ALL telegram-related packages")
    print("and reinstall only the correct version for Python 3.13.")
    print()
    
    # Step 1: Find all telegram packages
    print("🔍 Finding all telegram-related packages...")
    telegram_packages = find_telegram_packages()
    if telegram_packages:
        print(f"📦 Found packages: {', '.join(telegram_packages)}")
    else:
        print("📦 No telegram packages found")
    
    print()
    
    # Step 2: Uninstall all telegram packages
    packages_to_remove = [
        "python-telegram-bot",
        "telegram",
        "python-telegram-bot[all]",
        "python-telegram-bot[ext]",
        "telegram-bot",
        "telegram-sdk",
        "telegram-api"
    ]
    
    # Add any found packages
    packages_to_remove.extend(telegram_packages)
    
    # Remove duplicates
    packages_to_remove = list(set(packages_to_remove))
    
    for package in packages_to_remove:
        run_command(f"pip uninstall {package} -y", f"Uninstalling {package}")
    
    print()
    
    # Step 3: Clean pip cache and temporary files
    run_command("pip cache purge", "Clearing pip cache")
    run_command("pip cache info", "Checking cache status")
    
    print()
    
    # Step 4: Check for any remaining telegram imports
    print("🔍 Checking for remaining telegram imports...")
    try:
        import telegram
        print(f"❌ Still found telegram module: {telegram.__file__}")
        print("💡 This means there's still a conflicting package installed")
        
        # Try to find where it's coming from
        result = subprocess.run("python -c 'import telegram; print(telegram.__file__)'", 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"📍 Location: {result.stdout.strip()}")
            
            # Try to remove the directory
            telegram_path = result.stdout.strip()
            if telegram_path and os.path.exists(telegram_path):
                parent_dir = os.path.dirname(telegram_path)
                print(f"🗑️  Attempting to remove: {parent_dir}")
                try:
                    shutil.rmtree(parent_dir)
                    print("✅ Removed telegram directory")
                except Exception as e:
                    print(f"❌ Could not remove directory: {e}")
        
    except ImportError:
        print("✅ No telegram module found (good)")
    except Exception as e:
        print(f"❌ Error checking telegram module: {e}")
    
    print()
    
    # Step 5: Install the correct version
    print("📦 Installing python-telegram-bot==13.15...")
    success = run_command("pip install python-telegram-bot==13.15", "Installing python-telegram-bot 13.15")
    
    if success:
        print()
        print("✅ Installation completed successfully!")
        print()
        print("🧪 Testing the installation...")
        
        # Test import
        try:
            import telegram
            from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
            from telegram.ext import Application, CommandHandler, MessageHandler, filters
            print("✅ All imports successful!")
            print("✅ Bot should now work with Python 3.13")
            
            # Show the version
            result = subprocess.run("pip show python-telegram-bot", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("📋 Package info:")
                print(result.stdout)
            
        except ImportError as e:
            print(f"❌ Import test failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
        print()
        print("🎉 Telegram dependencies fixed successfully!")
        print("💡 You can now run: python bot_runner.py")
        return True
    else:
        print()
        print("❌ Installation failed!")
        print("💡 Try running: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 