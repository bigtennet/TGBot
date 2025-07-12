@echo off
echo ========================================
echo    Safeguard Bot Setup Script
echo ========================================
echo.

echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo To run the bot:
echo   venv\Scripts\activate.bat
echo   python bot_runner.py
echo.
echo To run the web app:
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
pause 