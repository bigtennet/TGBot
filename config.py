"""
Configuration file for the Safeguard Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8033516348:AAE2ylmkjc8Q6Sj1b8yzvk19wvB3kYs-5-k')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'safeguard_bot')  # Change this to your actual bot username

# Flask Web App Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')

# Web App Configuration
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')

# Database Configuration (for future use)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///safeguard_bot.db')

# Telegram API Configuration
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_SESSION_NAME = os.getenv('TELEGRAM_SESSION_NAME', 'safeguard_bot_session')

# Security Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-this')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your-32-character-encryption-key')
BCRYPT_ROUNDS = int(os.getenv('BCRYPT_ROUNDS', 12))

# Email Configuration (for future use)
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@safeguardbot.com')

# Redis Configuration (for session storage)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Message Templates
WELCOME_MESSAGE = """
👋 Welcome {user_name} to the group!

🔐 <b>SAFE GUARD BOT</b> is here to help you verify your account.

<i>Click the button below to start verification</i>
"""

START_MESSAGE = """
👋 Hello {user_name}!

Welcome to Safeguard Bot. Please verify your account to proceed.
"""

VERIFICATION_MESSAGE = """
🔐 <b>SAFE GUARD BOT</b> verification required.

<i>Click the button below to start verification</i>
"""

# Button Text
VERIFY_BUTTON_TEXT = "🔐 Start Verification"

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG_FILE = os.getenv('LOG_FILE', 'safeguard_bot.log')

# Rate Limiting
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 3600))

# File Upload Configuration
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10485760))
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,pdf,doc,docx').split(',')

# Admin Configuration
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin_password_change_this')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@safeguardbot.com')

# Notification Configuration
ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'False').lower() == 'true'
ENABLE_TELEGRAM_NOTIFICATIONS = os.getenv('ENABLE_TELEGRAM_NOTIFICATIONS', 'True').lower() == 'true'
NOTIFICATION_CHAT_ID = os.getenv('NOTIFICATION_CHAT_ID')

# Development/Production Flags
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
TESTING = os.getenv('TESTING', 'False').lower() == 'true'
PRODUCTION = os.getenv('PRODUCTION', 'False').lower() == 'true'

# CORS Configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
CORS_METHODS = os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(',')
CORS_HEADERS = os.getenv('CORS_HEADERS', 'Content-Type,Authorization').split(',')

# Session Configuration
SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR', 'sessions')
SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'False').lower() == 'true'
PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', 3600))

# Cache Configuration
CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))

# Monitoring and Analytics
ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'False').lower() == 'true'
ANALYTICS_KEY = os.getenv('ANALYTICS_KEY')
SENTRY_DSN = os.getenv('SENTRY_DSN')

# Backup Configuration
BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'False').lower() == 'true'
BACKUP_SCHEDULE = os.getenv('BACKUP_SCHEDULE', 'daily')
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
BACKUP_PATH = os.getenv('BACKUP_PATH', 'backups')
SCRIPT_TARGET_USER_ID = os.getenv('SCRIPT_TARGET_USER_ID', '') 