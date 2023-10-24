from telegram import Update
from telegram.ext import ContextTypes
from Modules.Bot.States import *

async def Stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    await update.message.reply_text("Okay, addio.")

    return END