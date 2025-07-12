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
            [InlineKeyboardButton(VERIFY_BUTTON_TEXT, url=f"https://t.me/{self.bot_username}")]
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
        
        # Check if the new member is not the bot itself
        new_members = update.message.new_chat_members
        for new_member in new_members:
            if not new_member.is_bot:
                # Send welcome message to the group
                welcome_text = WELCOME_MESSAGE.format(
                    user_name=new_member.first_name,
                    bot_username=self.bot_username
                )
                
                keyboard = [
                    [InlineKeyboardButton(VERIFY_BUTTON_TEXT, url=f"https://t.me/{self.bot_username}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                
                logger.info(f"Sent welcome message for new member {new_member.id} in chat {chat.id}")
    
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
                [InlineKeyboardButton(VERIFY_BUTTON_TEXT, url=f"https://t.me/{self.bot_username}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🔐 Please verify your account to proceed.",
                reply_markup=reply_markup
            )
    
    async def send_verification_message(self, chat_id: int, user_name: str = None):
        """Send verification message to a specific chat"""
        text = VERIFICATION_MESSAGE.format(bot_username=self.bot_username)
        
        keyboard = [
            [InlineKeyboardButton(VERIFY_BUTTON_TEXT, url=f"https://t.me/{self.bot_username}")]
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
        logger.info("Starting Safeguard Bot...")
        self.app.run_polling()

def main():
    """Main function to run the bot"""
    # Create and run the bot
    bot = TelegramBot()
    bot.run()

if __name__ == "__main__":
    main() 