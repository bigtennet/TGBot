#!/usr/bin/env python3
"""
Fix Telegram Dependencies Script

This script completely removes all conflicting Telegram packages and installs
the correct version for Python 3.13 compatibility.
"""

import subprocess
import sys
import os

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

def main():
    """Main function to fix Telegram dependencies"""
    print("🔧 Telegram Dependencies Fixer")
    print("=" * 50)
    print("This script will fix Python 3.13 compatibility issues")
    print("by removing conflicting packages and installing the correct version.")
    print()
    
    # Step 1: Uninstall all telegram-related packages
    packages_to_remove = [
        "python-telegram-bot",
        "telegram",
        "python-telegram-bot[all]",
        "python-telegram-bot[ext]"
    ]
    
    for package in packages_to_remove:
        run_command(f"pip uninstall {package} -y", f"Uninstalling {package}")
    
    print()
    
    # Step 2: Clean pip cache
    run_command("pip cache purge", "Clearing pip cache")
    
    print()
    
    # Step 3: Install the correct version
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