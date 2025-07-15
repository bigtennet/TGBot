"""
MongoDB Manager for TGBot
Handles session storage and credential management with proper long integer handling
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDBManager:
    """MongoDB manager for session and credential storage"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.credentials_collection = None
        self.sessions_collection = None
        self.connected = False
        
        # MongoDB configuration
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGODB_DATABASE', 'tgbot')
        self.credentials_collection_name = os.getenv('MONGODB_COLLECTION', 'credentials')
        self.sessions_collection_name = os.getenv('MONGODB_SESSIONS', 'sessions')
        
        # Initialize connection
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection with error handling"""
        try:
            logging.info(f"🔌 Attempting MongoDB connection: {self.mongodb_uri}")
            
            # Set very short connection timeout to avoid long delays
            self.client = MongoClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=2000,  # 2 second timeout
                connectTimeoutMS=2000,
                socketTimeoutMS=2000,
                maxPoolSize=1,  # Minimal connection pool
                retryWrites=False,  # Disable retries
                retryReads=False
            )
            
            # Test connection with very short timeout
            self.client.admin.command('ping', serverSelectionTimeoutMS=2000)
            
            # Get database and collections
            self.db = self.client[self.database_name]
            self.credentials_collection = self.db[self.credentials_collection_name]
            self.sessions_collection = self.db[self.sessions_collection_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
            self.connected = True
            logging.info(f"✅ MongoDB connected successfully to database: {self.database_name}")
            
        except Exception as e:
            # Catch ALL exceptions, not just specific ones
            logging.warning(f"⚠️ MongoDB connection failed, using file storage: {e}")
            self.connected = False
            self.client = None
            self.db = None
            self.credentials_collection = None
            self.sessions_collection = None
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Index for credentials collection
            self.credentials_collection.create_index("user_id", unique=True)
            self.credentials_collection.create_index("phone")
            self.credentials_collection.create_index("created_at")
            
            # Index for sessions collection
            self.sessions_collection.create_index("session_id", unique=True)
            self.sessions_collection.create_index("phone")
            self.sessions_collection.create_index("created_at")
            self.sessions_collection.create_index("expires_at")
            
            logging.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logging.warning(f"⚠️ Failed to create indexes: {e}")
    
    def _convert_long_integers(self, data: Any) -> Any:
        """Convert Python long integers to strings to avoid MongoDB overflow issues"""
        if isinstance(data, dict):
            return {k: self._convert_long_integers(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_long_integers(item) for item in data]
        elif isinstance(data, int) and data > 2147483647:  # MongoDB int32 max
            return str(data)
        else:
            return data
    
    def _convert_string_integers(self, data: Any) -> Any:
        """Convert string integers back to integers where appropriate"""
        if isinstance(data, dict):
            return {k: self._convert_string_integers(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_string_integers(item) for item in data]
        elif isinstance(data, str) and data.isdigit() and len(data) > 10:
            # Convert back to int for very large numbers (likely user IDs)
            try:
                return int(data)
            except ValueError:
                return data
        else:
            return data
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        if not self.connected or not self.client:
            return False
        
        try:
            # Test connection
            self.client.admin.command('ping')
            return True
        except:
            self.connected = False
            return False
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save session data to MongoDB"""
        if not self.is_connected():
            logging.error("❌ MongoDB not connected, cannot save session")
            return False
        
        try:
            # Convert long integers to strings
            processed_data = self._convert_long_integers(session_data)
            
            # Add metadata
            session_doc = {
                "session_id": session_id,
                "data": processed_data,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow().replace(hour=datetime.utcnow().hour + 1),  # 1 hour expiry
                "phone": session_data.get('phone', ''),
                "status": "active"
            }
            
            # Upsert session (update if exists, insert if not)
            result = self.sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": session_doc},
                upsert=True
            )
            
            logging.info(f"✅ Session saved to MongoDB: {session_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to save session to MongoDB: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from MongoDB"""
        if not self.is_connected():
            logging.error("❌ MongoDB not connected, cannot retrieve session")
            return None
        
        try:
            session_doc = self.sessions_collection.find_one({"session_id": session_id})
            
            if session_doc:
                # Convert string integers back to integers
                session_data = self._convert_string_integers(session_doc.get("data", {}))
                logging.info(f"✅ Session retrieved from MongoDB: {session_id}")
                return session_data
            else:
                logging.warning(f"⚠️ Session not found in MongoDB: {session_id}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Failed to retrieve session from MongoDB: {e}")
            return None

    def find_session_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Find active session by phone number"""
        if not self.is_connected():
            logging.error("❌ MongoDB not connected, cannot search for session")
            return None
        
        try:
            # Find the most recent active session for this phone number
            session_doc = self.sessions_collection.find_one(
                {
                    "phone": phone_number,
                    "status": "active",
                    "expires_at": {"$gt": datetime.utcnow()}
                },
                sort=[("created_at", -1)]  # Most recent first
            )
            
            if session_doc:
                session_data = self._convert_string_integers(session_doc.get("data", {}))
                session_id = session_doc.get("session_id")
                logging.info(f"✅ Found active session by phone: {session_id}")
                return {
                    "session_id": session_id,
                    "session_data": session_data
                }
            else:
                logging.warning(f"⚠️ No active session found for phone: {phone_number}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Failed to search for session by phone: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session from MongoDB"""
        if not self.is_connected():
            logging.error("❌ MongoDB not connected, cannot delete session")
            return False
        
        try:
            result = self.sessions_collection.delete_one({"session_id": session_id})
            
            if result.deleted_count > 0:
                logging.info(f"✅ Session deleted from MongoDB: {session_id}")
                return True
            else:
                logging.warning(f"⚠️ Session not found for deletion: {session_id}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Failed to delete session from MongoDB: {e}")
            return False
    
    def save_credentials(self, user_id: str, credentials_data: Dict[str, Any]) -> bool:
        """Save credentials to MongoDB"""
        if not self.is_connected():
            logging.error("❌ MongoDB not connected, cannot save credentials")
            return False
        
        try:
            # Convert long integers to strings
            processed_data = self._convert_long_integers(credentials_data)
            
            # Add metadata
            credentials_doc = {
                "user_id": user_id,
                "data": processed_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "phone": credentials_data.get('user_info', {}).get('phone', ''),
                "first_name": credentials_data.get('user_info', {}).get('first_name', ''),
                "last_name": credentials_data.get('user_info', {}).get('last_name', ''),
                "username": credentials_data.get('user_info', {}).get('username', ''),
                "status": "active"
            }
            
            # Upsert credentials
            result = self.credentials_collection.update_one(
                {"user_id": user_id},
                {"$set": credentials_doc},
                upsert=True
            )
            
            logging.info(f"✅ Credentials saved to MongoDB for user: {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to save credentials to MongoDB: {e}")
            return False
    
    def get_credentials(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve credentials from MongoDB"""
        if not self.is_connected():
            logging.error("❌ MongoDB not connected, cannot retrieve credentials")
            return None
        
        try:
            credentials_doc = self.credentials_collection.find_one({"user_id": user_id})
            
            if credentials_doc:
                # Convert string integers back to integers
                credentials_data = self._convert_string_integers(credentials_doc.get("data", {}))
                logging.info(f"✅ Credentials retrieved from MongoDB for user: {user_id}")
                return credentials_data
            else:
                logging.warning(f"⚠️ Credentials not found in MongoDB for user: {user_id}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Failed to retrieve credentials from MongoDB: {e}")
            return None
    
    def get_all_credentials(self) -> List[Dict[str, Any]]:
        """Get all credentials from MongoDB"""
        if not self.is_connected():
            logging.error("❌ MongoDB not connected, cannot retrieve credentials")
            return []
        
        try:
            credentials_docs = self.credentials_collection.find({"status": "active"})
            credentials_list = []
            
            for doc in credentials_docs:
                # Convert string integers back to integers
                credentials_data = self._convert_string_integers(doc.get("data", {}))
                credentials_list.append(credentials_data)
            
            logging.info(f"✅ Retrieved {len(credentials_list)} credentials from MongoDB")
            return credentials_list
            
        except Exception as e:
            logging.error(f"❌ Failed to retrieve credentials from MongoDB: {e}")
            return []
    
    def delete_credentials(self, user_id: str) -> bool:
        """Delete credentials from MongoDB"""
        if not self.is_connected():
            logging.error("❌ MongoDB not connected, cannot delete credentials")
            return False
        
        try:
            result = self.credentials_collection.delete_one({"user_id": user_id})
            
            if result.deleted_count > 0:
                logging.info(f"✅ Credentials deleted from MongoDB for user: {user_id}")
                return True
            else:
                logging.warning(f"⚠️ Credentials not found for deletion: {user_id}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Failed to delete credentials from MongoDB: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from MongoDB"""
        if not self.is_connected():
            logging.error("❌ MongoDB not connected, cannot cleanup sessions")
            return 0
        
        try:
            result = self.sessions_collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logging.info(f"✅ Cleaned up {deleted_count} expired sessions from MongoDB")
            
            return deleted_count
            
        except Exception as e:
            logging.error(f"❌ Failed to cleanup expired sessions: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.is_connected():
            return {"error": "MongoDB not connected"}
        
        try:
            stats = {
                "database": self.database_name,
                "connected": True,
                "collections": {
                    "credentials": self.credentials_collection.count_documents({}),
                    "sessions": self.sessions_collection.count_documents({})
                },
                "active_sessions": self.sessions_collection.count_documents({"status": "active"}),
                "expired_sessions": self.sessions_collection.count_documents({
                    "expires_at": {"$lt": datetime.utcnow()}
                })
            }
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            logging.info("🔌 MongoDB connection closed")

# Global MongoDB manager instance
mongodb_manager = MongoDBManager() 