#!/usr/bin/env python3
"""
Script to check bot permissions in a Telegram group
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')

def get_chat_member(chat_id, user_id):
    """Get information about a member in a chat"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    data = {
        'chat_id': chat_id,
        'user_id': user_id
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def get_bot_info():
    """Get bot information"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"❌ Error getting bot info: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("🔍 Bot Permission Checker")
    print("=" * 40)
    
    # Get bot info
    bot_info = get_bot_info()
    if not bot_info:
        print("❌ Could not get bot information")
        return
    
    bot_id = bot_info['id']
    bot_username = bot_info['username']
    
    print(f"🤖 Bot: @{bot_username} (ID: {bot_id})")
    print()
    
    # Get group ID from user
    group_id = input("Enter the group ID (e.g., -4838752549): ").strip()
    
    if not group_id:
        print("❌ No group ID provided")
        return
    
    try:
        group_id = int(group_id)
    except ValueError:
        print("❌ Invalid group ID. Please enter a valid number.")
        return
    
    print(f"\n🔍 Checking permissions in group {group_id}...")
    
    # Get bot's member info
    member_info = get_chat_member(group_id, bot_id)
    
    if not member_info:
        print("❌ Could not get member information")
        return
    
    status = member_info.get('status', 'unknown')
    permissions = member_info.get('permissions', {})
    
    print(f"\n📊 Bot Status: {status}")
    print(f"📋 Permissions:")
    
    if status == 'administrator':
        admin_permissions = member_info.get('can_post_messages', False)
        print(f"   ✅ Can post messages: {admin_permissions}")
        print(f"   ✅ Can edit messages: {member_info.get('can_edit_messages', False)}")
        print(f"   ✅ Can delete messages: {member_info.get('can_delete_messages', False)}")
        print(f"   ✅ Can pin messages: {member_info.get('can_pin_messages', False)}")
        print(f"   ✅ Can invite users: {member_info.get('can_invite_users', False)}")
        print(f"   ✅ Can restrict members: {member_info.get('can_restrict_members', False)}")
        print(f"   ✅ Can promote members: {member_info.get('can_promote_members', False)}")
        print(f"   ✅ Can change info: {member_info.get('can_change_info', False)}")
        print(f"   ✅ Is anonymous: {member_info.get('is_anonymous', False)}")
        
        if not admin_permissions:
            print("\n⚠️  WARNING: Bot cannot post messages!")
            print("💡 Solution: Enable 'Post Messages' permission in group settings")
    elif status == 'member':
        print("   ❌ Bot is only a member, not an admin")
        print("   💡 Solution: Make bot an administrator")
    elif status == 'left':
        print("   ❌ Bot has left the group")
        print("   💡 Solution: Add bot back to the group")
    elif status == 'kicked':
        print("   ❌ Bot was kicked from the group")
        print("   💡 Solution: Add bot back to the group")
    else:
        print(f"   ❓ Unknown status: {status}")

if __name__ == "__main__":
    main() 