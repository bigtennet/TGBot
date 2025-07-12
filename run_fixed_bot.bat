@echo off
echo ========================================
echo Running FIXED Telegram Bot
echo ========================================
echo.
echo This version automatically detects HTTP URLs and
echo sends messages without inline keyboard buttons.
echo.
echo No environment variables needed!
echo.

cd /d "%~dp0"
python bot_http_fixed.py

pause 