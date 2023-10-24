from telegram import Update
from telegram.ext import ContextTypes
from Modules.Bot.States import *

async def End(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation from InlineKeyboardButton."""
    await update.callback_query.answer()

    text = "👋🏽 Arrivederci, buon caffè! 👋🏽"
    await update.callback_query.edit_message_text(text=text)

    return END