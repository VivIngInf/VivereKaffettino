from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from Modules.Bot.States import *


async def Stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    # Tolgo lo stato iniziale dal dizionario
    if list(context.user_data.keys()).count("first_start") > 0:
        context.user_data.pop("first_start")
        await update.callback_query.edit_message_text(text="👋🏽 Arrivederci, buon caffè! 👋🏽")
        return ConversationHandler.END
