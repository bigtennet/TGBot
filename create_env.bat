@echo off
echo ========================================
echo    Creating .env file from template
echo ========================================
echo.

if exist .env (
    echo .env file already exists!
    echo Do you want to overwrite it? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        copy env_template.txt .env
        echo .env file created successfully!
    ) else (
        echo Operation cancelled.
    )
) else (
    copy env_template.txt .env
    echo .env file created successfully!
)

echo.
echo ========================================
echo    Next Steps:
echo ========================================
echo 1. Edit .env file with your actual values
echo 2. Change BOT_USERNAME to your bot username
echo 3. Update SECRET_KEY for security
echo 4. Run: venv\Scripts\activate.bat
echo 5. Run: pip install -r requirements.txt
echo 6. Run: python bot_runner.py
echo.
pause 