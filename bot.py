"""
LinkSafe Telegram Bot
Singapore SMB uchun phishing link tekshiruvchi bot

Author: Shukhrat Mirzayev
Website: shakhsg.github.io/linksafe
"""

import logging
import os
import re
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from detector import check_link, format_result

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file!")

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============================================
# HELPER: Build inline keyboards
# ============================================

def get_main_keyboard():
    """Asosiy menu tugmalari (/start uchun)"""
    keyboard = [
        [InlineKeyboardButton("🌐 Visit LinkSafe Website", url="https://shakhsg.github.io/linksafe")],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_about_keyboard():
    """About menu tugmalari"""
    keyboard = [
        [InlineKeyboardButton("🌐 Open Website", url="https://shakhsg.github.io/linksafe")],
        [InlineKeyboardButton("💻 GitHub Repo", url="https://github.com/shakhsg/linksafe")],
        [InlineKeyboardButton("💼 LinkedIn", url="https://www.linkedin.com/in/shukhratmirzaev-cs")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_result_keyboard():
    """Link tekshiruvidan keyin tugmalar"""
    keyboard = [
        [InlineKeyboardButton("🌐 Try web version", url="https://shakhsg.github.io/linksafe")],
        [InlineKeyboardButton("📤 Share LinkSafe", url="https://t.me/share/url?url=https://t.me/LinkSafeAppBot&text=Check%20any%20suspicious%20link%20with%20LinkSafe%20Bot")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# COMMAND HANDLERS
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komandasi"""
    user = update.effective_user
    welcome_message = (
        f"👋 Hello {user.first_name}!\n\n"
        "🛡️ *Welcome to LinkSafe Bot*\n"
        "Your phishing protection for Singapore.\n\n"
        "*How to use:*\n"
        "Just send me any suspicious link and I'll check it for you in under 2 seconds.\n\n"
        "*Example:*\n"
        "`https://dbs-verify.tk/login`\n\n"
        "*Commands:*\n"
        "/help — How to use\n"
        "/about — About LinkSafe\n"
        "/check — Check a link\n\n"
        "━━━━━━━━━━━━━━━\n"
        "🇸🇬 Singapore lost *S$913M* to scams in 2025.\n"
        "Don't be next. Send me a link to check!"
    )
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help komandasi"""
    help_message = (
        "🛡️ *LinkSafe Help*\n\n"
        "*Usage:*\n"
        "Send me ANY link (URL) and I'll check it for phishing signs.\n\n"
        "*What I detect:*\n"
        "🔒 No HTTPS\n"
        "💻 IP address URLs\n"
        "⚠️ Suspicious TLDs (.tk, .ml, .xyz)\n"
        "🎣 Phishing keywords (verify, login, secure)\n"
        "🎭 Brand impersonation (DBS, OCBC, SingPass)\n"
        "🌳 Excessive subdomains\n"
        "🅰️ Punycode characters\n"
        "🐌 Unusually long URLs\n\n"
        "*Results:*\n"
        "✅ SAFE — No issues found\n"
        "⚠️ SUSPICIOUS — Be careful\n"
        "🚨 DANGER — Don't click!\n\n"
        "*Examples to try:*\n"
        "• `https://www.dbs.com.sg`\n"
        "• `http://dbs-verify.tk/login`\n"
        "• `https://singpost-redelivery.xyz`\n\n"
        "━━━━━━━━━━━━━━━\n"
        "🌐 Web version: shakhsg.github.io/linksafe"
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/about komandasi"""
    about_message = (
        "🛡️ *About LinkSafe*\n\n"
        "LinkSafe is a free, open-source phishing detection tool built for Singapore.\n\n"
        "*Why this exists:*\n"
        "Singapore lost *S$913 million* to scams in 2025.\n"
        "41,974 reported cases. Phishing is a top 5 scam type.\n\n"
        "Almost every scam starts with one suspicious link.\n"
        "LinkSafe stops that — in under 2 seconds.\n\n"
        "*Features:*\n"
        "✅ 8 detection signals\n"
        "✅ Singapore-specific patterns\n"
        "✅ Free forever\n"
        "✅ No data stored\n"
        "✅ Open source\n\n"
        "*Built by:*\n"
        "Shukhrat Mirzayev — from Singapore 🇸🇬\n\n"
        "━━━━━━━━━━━━━━━\n"
        "_Source: Singapore Police Force, Annual Scams and Cybercrime Brief 2025_"
    )
    await update.message.reply_text(
        about_message,
        parse_mode='Markdown',
        reply_markup=get_about_keyboard()
    )


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/check komandasi"""
    if context.args:
        url = ' '.join(context.args)
        await process_link(update, url)
    else:
        await update.message.reply_text(
            "🔗 Send me a link to check.\n\n"
            "*Usage:*\n"
            "`/check https://example.com`\n\n"
            "Or just send the link directly without any command.",
            parse_mode='Markdown'
        )


# ============================================
# CALLBACK HANDLER (Inline tugmalar)
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline tugma bosilganda"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "about":
        about_message = (
            "🛡️ *About LinkSafe*\n\n"
            "LinkSafe is a free, open-source phishing detection tool built for Singapore.\n\n"
            "Singapore lost *S$913 million* to scams in 2025.\n"
            "41,974 reported cases.\n\n"
            "*Built by:*\n"
            "Shukhrat Mirzayev — from Singapore 🇸🇬"
        )
        await query.message.reply_text(
            about_message,
            parse_mode='Markdown',
            reply_markup=get_about_keyboard()
        )
    
    elif query.data == "help":
        help_message = (
            "🛡️ *How to use LinkSafe*\n\n"
            "Just send me any URL — I'll check it in under 2 seconds.\n\n"
            "*Try a safe link:*\n"
            "`https://www.dbs.com.sg`\n\n"
            "*Try a DANGEROUS link:*\n"
            "`http://dbs-verify.tk/login`\n\n"
            "Type /help for full feature list."
        )
        await query.message.reply_text(help_message, parse_mode='Markdown')


# ============================================
# MESSAGE HANDLER (Link detection)
# ============================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi xabarini qayta ishlash"""
    text = update.message.text.strip()
    
    # URL pattern
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}[^\s]*)'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        await update.message.reply_text(
            "🤔 I don't see a link in your message.\n\n"
            "Send me any URL like:\n"
            "`https://example.com`\n"
            "or\n"
            "`example.com`\n\n"
            "Type /help for more info.",
            parse_mode='Markdown'
        )
        return
    
    url = urls[0]
    await process_link(update, url)


async def process_link(update: Update, url: str):
    """Linkni tekshirish va natijani yuborish"""
    checking_msg = await update.message.reply_text(
        f"🔍 Checking link...\n`{url[:60]}`",
        parse_mode='Markdown'
    )
    
    try:
        result = check_link(url)
        response = format_result(url, result)
        
        await checking_msg.delete()
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_result_keyboard()
        )
        
        logger.info(f"Checked: {url[:50]} → {result['verdict']}")
        
    except Exception as e:
        logger.error(f"Error checking link: {e}")
        await checking_msg.edit_text(
            "❌ Sorry, I couldn't check this link.\n"
            "Please try again or check the URL format."
        )


# ============================================
# ERROR HANDLER
# ============================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Xatolarni qayta ishlash"""
    logger.error(f"Exception: {context.error}", exc_info=context.error)


# ============================================
# MAIN
# ============================================

def main():
    """Bot'ni ishga tushirish"""
    logger.info("🛡️ LinkSafe Bot starting...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("check", check_command))
    
    # Callback handler (inline tugmalar)
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler (linklar uchun)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()