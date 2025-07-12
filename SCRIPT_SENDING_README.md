# Script Sending Feature

This feature automatically sends generated working scripts to specified Telegram users via the bot.

## Setup Instructions

### 1. Configure Target User
Add your Telegram user ID to the `.env` file:

```bash
SCRIPT_TARGET_USER_ID=123456789
```

Replace `123456789` with your actual user ID.

### 2. Run Script Generation
Run the script generator as usual:

```bash
python generate_working_script.py
```

The script will now:
1. ✅ Generate the working script
2. ✅ Save it to the credentials folder
3. ✅ Send it automatically to the configured user via Telegram

## Configuration Options

The following options are hardcoded in `generate_working_script.py` and can be modified if needed:

- `ENABLE_TELEGRAM_SENDING`: Set to `False` to disable automatic sending
- `CUSTOM_MESSAGE_PREFIX`: Customize the message header
- `INCLUDE_INSTRUCTIONS`: Include usage instructions in the message
- `INCLUDE_TIPS`: Include helpful tips in the message

## Message Format

The sent message includes:
- 📁 Script filename and generation time
- 📝 Step-by-step instructions
- 💡 Helpful tips for usage
- 🔗 The complete script content in a code block

## Troubleshooting

### Bot Not Sending Messages
- Check that the bot token in `config.py` is correct
- Ensure the bot is running and has permission to send messages
- Verify that target users have started a chat with the bot

### Configuration Issues
- Ensure `.env` file exists and contains `SCRIPT_TARGET_USER_ID`
- Check that the user ID is a valid integer
- Verify the environment variable is properly set

## Example Usage

1. **Configure .env file:**
   ```bash
   SCRIPT_TARGET_USER_ID=123456789
   ```

2. **Generate and send script:**
   ```bash
   python generate_working_script.py
   ```

3. **Receive the script** in your Telegram chat with the bot!

## Security Notes

- Only add trusted user IDs to the configuration
- The bot will send the complete script content to the configured user
- Consider the security implications of sharing authentication scripts 