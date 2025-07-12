@echo off
echo ========================================
echo Fixing Telegram Bot URL Issue
echo ========================================
echo.
echo Setting LOCAL_DEV=true to fix inline keyboard issue...
echo.

set LOCAL_DEV=true
set WEBAPP_URL=http://localhost:5000

echo Environment variables set:
echo - LOCAL_DEV=%LOCAL_DEV%
echo - WEBAPP_URL=%WEBAPP_URL%
echo.

echo Starting bot in local development mode...
echo The bot will send messages without inline keyboard buttons.
echo Users will see the verification URL in the message text.
echo.

cd /d "%~dp0"
python bot_http.py

pause 