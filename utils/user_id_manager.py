import os
import json
import logging
from typing import List, Optional
import datetime

logger = logging.getLogger(__name__)

class UserIDManager:
    def __init__(self, file_path: str = "config/user_ids.json"):
        self.file_path = file_path
        self._ensure_config_dir()
        self._load_user_ids()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists"""
        dir_path = os.path.dirname(self.file_path)
        if dir_path:  # Only create directory if there's a path
            os.makedirs(dir_path, exist_ok=True)
    
    def _load_user_ids(self):
        """Load user IDs from file"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_ids = data.get('user_ids', [])
                    logger.info(f"Loaded {len(self.user_ids)} user IDs from {self.file_path}")
            else:
                self.user_ids = []
                self._save_user_ids()
                logger.info(f"Created new user IDs file at {self.file_path}")
        except Exception as e:
            logger.error(f"Error loading user IDs: {e}")
            self.user_ids = []
    
    def _save_user_ids(self):
        """Save user IDs to file"""
        try:
            data = {
                'user_ids': self.user_ids,
                'last_updated': str(datetime.datetime.now())
            }
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.user_ids)} user IDs to {self.file_path}")
        except Exception as e:
            logger.error(f"Error saving user IDs: {e}")
    
    def add_user_id(self, user_id: str) -> bool:
        """Add a user ID to the list"""
        try:
            # Clean the user ID (remove any whitespace)
            user_id = str(user_id).strip()
            
            # Check if it's a valid user ID (should be numeric)
            if not user_id.isdigit():
                logger.warning(f"Invalid user ID format: {user_id}")
                return False
            
            # Check if user ID already exists
            if user_id in self.user_ids:
                logger.info(f"User ID {user_id} already exists")
                return False
            
            self.user_ids.append(user_id)
            self._save_user_ids()
            logger.info(f"Added user ID: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding user ID {user_id}: {e}")
            return False
    
    def delete_user_id(self, user_id: str) -> bool:
        """Delete a user ID from the list"""
        try:
            user_id = str(user_id).strip()
            
            if user_id not in self.user_ids:
                logger.info(f"User ID {user_id} not found in list")
                return False
            
            self.user_ids.remove(user_id)
            self._save_user_ids()
            logger.info(f"Deleted user ID: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user ID {user_id}: {e}")
            return False
    
    def get_user_ids(self) -> List[str]:
        """Get all user IDs"""
        return self.user_ids.copy()
    
    def user_id_exists(self, user_id: str) -> bool:
        """Check if a user ID exists in the list"""
        return str(user_id).strip() in self.user_ids
    
    def get_user_ids_count(self) -> int:
        """Get the count of user IDs"""
        return len(self.user_ids) 