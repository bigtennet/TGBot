# MongoDB Session Storage Integration

## Overview

This project now uses MongoDB to store Telegram authentication sessions instead of in-memory storage. This resolves the session expiration issues that occur when the application restarts on cloud platforms like Render.

## Problem Solved

**Before MongoDB Integration:**
- Sessions were stored in memory (`self.active_sessions`)
- When the application restarted, all sessions were lost
- Users would get "Session expired" errors even with valid codes
- This was particularly problematic on cloud platforms with frequent restarts

**After MongoDB Integration:**
- Sessions are persisted in MongoDB database
- Sessions survive application restarts
- Automatic session expiration with TTL indexes
- Fallback to in-memory storage if MongoDB is unavailable

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://emmanuelcyril36:CZ8YhuwCWlC7F34l@cluster0.goczidb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DB_NAME=safeguard_bot
MONGODB_SESSIONS_COLLECTION=telegram_sessions
SESSION_EXPIRY_MINUTES=5
```

### Dependencies

The following dependency has been added to `requirements.txt`:
```
pymongo==4.6.1
```

## Architecture

### Components

1. **MongoSessionManager** (`utils/mongo_session_manager.py`)
   - Handles MongoDB connection and session operations
   - Provides fallback to in-memory storage
   - Automatic session expiration with TTL indexes

2. **Updated TelegramAuth** (`utils/tg/auth.py`)
   - Uses MongoDB for session storage instead of in-memory
   - Maintains backward compatibility
   - Enhanced error handling

3. **Updated Main App** (`main.py`)
   - Integrates MongoDB session manager
   - Proper cleanup on shutdown

### Session Data Structure

Sessions are stored with the following structure in MongoDB:

```json
{
  "session_id": "session_+1234567890_abc123",
  "phone_number": "+1234567890",
  "phone_code_hash": "telegram_phone_code_hash",
  "client_data": {
    "api_id": "your_api_id",
    "api_hash": "your_api_hash",
    "session_string": "telethon_session_string",
    "is_connected": false
  },
  "created_at": "2025-01-13T15:30:00Z",
  "expires_at": "2025-01-13T15:35:00Z",
  "last_accessed": "2025-01-13T15:32:00Z"
}
```

## Features

### Automatic Session Expiration
- Sessions automatically expire after 5 minutes (configurable)
- MongoDB TTL indexes handle cleanup automatically
- Manual cleanup also available

### Fallback Storage
- If MongoDB is unavailable, falls back to in-memory storage
- Seamless degradation ensures service availability
- Automatic reconnection attempts

### Connection Management
- Connection pooling for better performance
- Automatic reconnection on connection loss
- Proper cleanup on application shutdown

## Testing

Run the MongoDB integration test:

```bash
python test_mongodb_session.py
```

This will test:
- MongoDB connection
- Session storage and retrieval
- Session deletion
- Cleanup operations
- Connection closure

## Deployment

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`
3. Run the application: `python main.py`

### Cloud Deployment (Render)
1. Add MongoDB environment variables to your Render service
2. Deploy the updated code
3. Sessions will now persist across restarts

## Monitoring

### Logs
The application logs MongoDB operations:
- Connection status
- Session storage/retrieval
- Cleanup operations
- Error handling

### Metrics
- Active session count
- Connection status
- Error rates

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check network connectivity
   - Verify MongoDB URI
   - Check credentials

2. **Session Still Expiring**
   - Verify MongoDB is connected
   - Check session expiry settings
   - Review application logs

3. **Performance Issues**
   - Check MongoDB indexes
   - Monitor connection pool size
   - Review session cleanup frequency

### Debug Mode

Enable debug logging by setting:
```python
logging.getLogger('utils.mongo_session_manager').setLevel(logging.DEBUG)
```

## Security Considerations

- MongoDB connection uses SSL/TLS
- Credentials are stored in environment variables
- Session data is encrypted in transit
- Automatic session expiration prevents data accumulation

## Migration from In-Memory Storage

The integration is backward compatible. Existing code will continue to work, but sessions will now be persisted in MongoDB instead of memory.

## Future Enhancements

- Session analytics and monitoring
- Multi-region MongoDB deployment
- Advanced session management features
- Performance optimizations 