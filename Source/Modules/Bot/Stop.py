from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from Modules.Bot.States import *

async def Stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    # Tolgo lo stato iniziale dal dizionario
    context.user_data.pop("first_start")
    await update.callback_query.edit_message_text("Okay, addio.")
    return ConversationHandler.END