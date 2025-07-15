import os
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class MongoSessionManager:
    def __init__(self):
        """Initialize MongoDB session manager"""
        self.client = None
        self.db = None
        self.sessions_collection = None
        self.connected = False
        
        # MongoDB connection string
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://emmanuelcyril36:CZ8YhuwCWlC7F34l@cluster0.goczidb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        self.db_name = os.getenv('MONGODB_DB_NAME', 'safeguard_bot')
        self.collection_name = os.getenv('MONGODB_SESSIONS_COLLECTION', 'telegram_sessions')
        
        # Session expiration time (5 minutes)
        self.session_expiry_minutes = int(os.getenv('SESSION_EXPIRY_MINUTES', '5'))
        
        # Initialize connection
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            logger.info(f"🔌 Connecting to MongoDB: {self.mongo_uri[:50]}...")
            
            # Connect with timeout and retry settings
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=10,
                retryWrites=True
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[self.db_name]
            self.sessions_collection = self.db[self.collection_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
            self.connected = True
            logger.info(f"✅ Successfully connected to MongoDB database: {self.db_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            self.connected = False
            # Fall back to in-memory storage
            self._fallback_storage = {}
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
            self.connected = False
            self._fallback_storage = {}
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Index on session_id for fast lookups
            self.sessions_collection.create_index("session_id", unique=True)
            
            # Index on created_at for cleanup operations
            self.sessions_collection.create_index("created_at")
            
            # Index on phone_number for phone-based queries
            self.sessions_collection.create_index("phone_number")
            
            # TTL index to automatically expire old sessions
            self.sessions_collection.create_index(
                "created_at", 
                expireAfterSeconds=self.session_expiry_minutes * 60
            )
            
            logger.info("✅ MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating MongoDB indexes: {e}")
    
    def _ensure_connection(self):
        """Ensure MongoDB connection is active"""
        if not self.connected:
            self._connect()
        return self.connected
    
    def _convert_large_ints_to_str(self, obj):
        """Recursively convert large ints (>2**31-1) to strings in a dict/list"""
        if isinstance(obj, dict):
            return {k: self._convert_large_ints_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_large_ints_to_str(v) for v in obj]
        elif isinstance(obj, int) and abs(obj) > 2**31-1:
            return str(obj)
        else:
            return obj

    def store_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Store a session in MongoDB"""
        if not self._ensure_connection():
            # Fall back to in-memory storage
            self._fallback_storage[session_id] = {
                **session_data,
                'created_at': datetime.utcnow(),
            }
            logger.warning(f"⚠️ Using fallback in-memory storage for session: {session_id}")
            return True
        try:
            # Convert large ints to strings in session_data
            safe_session_data = self._convert_large_ints_to_str(session_data)
            # Prepare session document - store session string for client recreation
            session_doc = {
                'session_id': session_id,
                'phone_number': safe_session_data.get('phone_number'),
                'phone_code_hash': safe_session_data.get('phone_code_hash'),
                'session_string': safe_session_data.get('session_string'),
                'created_at': datetime.utcnow(),
                'last_accessed': datetime.utcnow()
            }
            # Store the rest of the session data (if any) in a subdocument
            for k, v in safe_session_data.items():
                if k not in session_doc:
                    session_doc[k] = v
            # DEBUG: Log the session_doc before storing
            import pprint
            logger.debug(f"Session doc to be stored in MongoDB: {pprint.pformat(session_doc)}")
            # Use upsert to handle both insert and update
            result = self.sessions_collection.update_one(
                {'session_id': session_id},
                {'$set': session_doc},
                upsert=True
            )
            logger.info(f"✅ Session stored in MongoDB: {session_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error storing session {session_id} in MongoDB: {e}")
            # Fall back to in-memory storage
            self._fallback_storage[session_id] = {
                **session_data,
                'created_at': datetime.utcnow(),
            }
            return True
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session from MongoDB"""
        if not self._ensure_connection():
            # Check fallback storage
            session_data = self._fallback_storage.get(session_id)
            if session_data:
                return session_data
            return None
        
        try:
            # Find session document
            session_doc = self.sessions_collection.find_one({'session_id': session_id})
            
            if not session_doc:
                logger.warning(f"⚠️ Session not found in MongoDB: {session_id}")
                return None
            
            # Update last accessed time
            self.sessions_collection.update_one(
                {'session_id': session_id},
                {'$set': {'last_accessed': datetime.utcnow()}}
            )
            
            # Reconstruct session data - include session string for client recreation
            session_data = {
                'phone_number': session_doc['phone_number'],
                'phone_code_hash': session_doc['phone_code_hash'],
                'session_string': session_doc.get('session_string'),
                'created_at': session_doc['created_at']
            }
            
            logger.info(f"✅ Session retrieved from MongoDB: {session_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"❌ Error retrieving session {session_id} from MongoDB: {e}")
            # Check fallback storage
            session_data = self._fallback_storage.get(session_id)
            if session_data:
                return session_data
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session from MongoDB"""
        if not self._ensure_connection():
            # Remove from fallback storage
            self._fallback_storage.pop(session_id, None)
            return True
        
        try:
            result = self.sessions_collection.delete_one({'session_id': session_id})
            logger.info(f"✅ Session deleted from MongoDB: {session_id}")
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error deleting session {session_id} from MongoDB: {e}")
            # Remove from fallback storage
            self._fallback_storage.pop(session_id, None)
            return True
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from MongoDB"""
        if not self._ensure_connection():
            # Clean up fallback storage
            current_time = datetime.utcnow()
            expired_keys = [
                key for key, data in self._fallback_storage.items()
                if data['created_at'] < current_time
            ]
            for key in expired_keys:
                del self._fallback_storage[key]
            return len(expired_keys)
        
        try:
            # Delete sessions that have expired
            result = self.sessions_collection.delete_many({
                'created_at': {'$lt': datetime.utcnow()}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} expired sessions from MongoDB")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired sessions from MongoDB: {e}")
            return 0
    
    def _serialize_client_data(self, client) -> Dict[str, Any]:
        """Serialize Telethon client data for MongoDB storage"""
        if not client:
            return {}
        
        try:
            # Extract essential client data that can be serialized
            client_data = {
                'api_id': getattr(client, 'api_id', None),
                'api_hash': getattr(client, 'api_hash', None),
                'session_string': getattr(client.session, 'save', lambda: '')() if hasattr(client, 'session') else '',
                'is_connected': getattr(client, 'is_connected', lambda: False)()
            }
            return client_data
        except Exception as e:
            logger.error(f"❌ Error serializing client data: {e}")
            return {}
    
    def _deserialize_client_data(self, client_data: Dict[str, Any]):
        """Deserialize client data from MongoDB"""
        # Note: We can't fully reconstruct the Telethon client from stored data
        # This is mainly for metadata storage. The actual client recreation
        # should be handled by the auth system when needed.
        return client_data
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        if not self._ensure_connection():
            return len(self._fallback_storage)
        
        try:
            return self.sessions_collection.count_documents({
                'created_at': {'$gt': datetime.utcnow()}
            })
        except Exception as e:
            logger.error(f"❌ Error getting session count from MongoDB: {e}")
            return len(self._fallback_storage)
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            try:
                self.client.close()
                logger.info("✅ MongoDB connection closed")
            except Exception as e:
                logger.error(f"❌ Error closing MongoDB connection: {e}")

# Global instance
mongo_session_manager = MongoSessionManager() 