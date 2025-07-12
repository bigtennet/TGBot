@echo off
echo Starting HTTP Telegram Bot in Local Development Mode...
echo.
echo This mode will send messages without inline keyboard buttons
echo since Telegram requires HTTPS URLs for inline keyboards.
echo.
echo Make sure your Flask web app is running on http://localhost:5000
echo.
pause

set LOCAL_DEV=true
cd /d "%~dp0"
python bot_http.py

pause 