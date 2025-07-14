#!/usr/bin/env python3
"""
Check available sessions and their ages
"""

import os
import json
from datetime import datetime

def check_sessions():
    """Check available credential sessions"""
    credentials_dir = "credentials"
    
    if not os.path.exists(credentials_dir):
        print("❌ No credentials directory found")
        return
    
    # Get all JSON files
    json_files = [f for f in os.listdir(credentials_dir) if f.endswith('.json')]
    
    if not json_files:
        print("❌ No credential files found")
        return
    
    # Sort by modification time
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(credentials_dir, x)), reverse=True)
    
    print(f"📁 Found {len(json_files)} credential files:")
    print("=" * 80)
    
    for i, filename in enumerate(json_files[:10]):  # Show top 10
        filepath = os.path.join(credentials_dir, filename)
        mtime = os.path.getmtime(filepath)
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        
        # Load file to get user info
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            user_info = data.get('user_info', {})
            user_name = f"{user_info.get('first_name', 'Unknown')} {user_info.get('last_name', '')}".strip()
            user_phone = user_info.get('phone', 'Unknown')
            user_id = user_info.get('id', 'Unknown')
            
            print(f"{i+1:2d}. {filename}")
            print(f"    👤 User: {user_name} (+{user_phone})")
            print(f"    🆔 ID: {user_id}")
            print(f"    ⏰ Age: {age_hours:.1f} hours ago")
            print(f"    📅 Created: {datetime.fromtimestamp(mtime)}")
            print()
            
        except Exception as e:
            print(f"{i+1:2d}. {filename} (Error reading: {e})")
            print()

if __name__ == "__main__":
    check_sessions() 