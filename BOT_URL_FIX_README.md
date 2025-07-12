# Telegram Bot URL Fix

## Problem
The bot was failing to send welcome messages with inline keyboard buttons because Telegram requires HTTPS URLs for inline keyboard buttons, but the bot was using `http://localhost:5000`.

## Solution
The bot now supports both local development and production modes:

### For Local Development
1. Set `LOCAL_DEV=true` in your `.env` file
2. Run the bot using `run_http_bot_local.bat`
3. The bot will send messages without inline keyboard buttons, but include the URL in the message text

### For Production
1. Set `LOCAL_DEV=false` in your `.env` file
2. Set `WEBAPP_URL=https://your-domain.com` in your `.env` file
3. Run the bot using `run_http_bot.bat`
4. The bot will send messages with inline keyboard buttons

## Quick Fix for Current Issue
To fix the current error immediately:

1. **Option 1: Use Local Development Mode**
   ```bash
   # Add to your .env file:
   LOCAL_DEV=true
   WEBAPP_URL=http://localhost:5000
   ```

2. **Option 2: Use Production URL**
   ```bash
   # Add to your .env file:
   LOCAL_DEV=false
   WEBAPP_URL=https://safeguard-bot.vercel.app
   ```

## Running the Bot
- **Local Development**: `run_http_bot_local.bat`
- **Production**: `run_http_bot.bat`

## What Changed
- Added `LOCAL_DEV` environment variable
- Modified welcome message logic to handle both modes
- Created separate batch file for local development
- Updated default WEBAPP_URL to use HTTPS 