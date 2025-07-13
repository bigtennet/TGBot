@echo off
echo ========================================
echo Telegram Bot Conflict Fixer
echo ========================================
echo.
echo This will fix the "Conflict: terminated by other getUpdates request" error
echo by clearing webhooks and checking for multiple instances.
echo.

REM Install psutil if not already installed
echo Installing required packages...
pip install psutil requests python-dotenv

echo.
echo Checking for running bot processes...
python check_bot_processes.py

echo.
echo Running conflict fix...
python fix_bot_conflict.py

echo.
echo Fix completed! You can now start your bot.
pause 