from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from Modules.Bot.New_Menu.Utility import *


async def stop_after_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force to end the conversation"""
    # Tolgo lo stato iniziale dal dizionario
    if "first_start" in context.user_data:
        for _class in CONVERSATION_CLASSES:
            if _class in context.user_data:
                context.user_data.pop(_class)
        context.user_data.pop("first_start")
        context.user_data.pop("initial_message")
        await update.callback_query.edit_message_text(
            text="Ti sei registrato correttamente, presto verrai verificato da un Admin")
        return ConversationHandler.END


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation manually"""
    # Tolgo lo stato iniziale dal dizionario
    if "first_start" in context.user_data:
        for _class in CONVERSATION_CLASSES:
            if _class in context.user_data:
                context.user_data.pop(_class)
        context.user_data.pop("first_start")
        context.user_data.pop("initial_message")
        await update.callback_query.edit_message_text(text="👋🏽 Arrivederci, buon caffè! 👋🏽")
        return ConversationHandler.END


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation by user command"""
    # Tolgo lo stato iniziale dal dizionario
    if "first_start" in context.user_data:
        context.user_data.pop("first_start")
        await context.bot.edit_message_text(chat_id=update.message.chat_id,
                                            message_id=context.user_data["initial_message"].message_id,
                                            text="👋🏽 Arrivederci, buon caffè! 👋🏽")
        for _class in CONVERSATION_CLASSES:
            if _class in context.user_data:
                context.user_data.pop(_class)

        context.user_data.pop("initial_message")
        return ConversationHandler.END


async def stop_to_restart_again(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation manually by button"""
    # Tolgo lo stato iniziale dal dizionario
    if "first_start" in context.user_data:
        for _class in CONVERSATION_CLASSES:
            if _class in context.user_data:
                context.user_data.pop(_class)
        context.user_data.pop("first_start")
        context.user_data.pop("initial_message")
        await update.callback_query.edit_message_text(
            text="Hai annullato la registrazione 😢. Non andartene, premi /start e ricominciamo 😊")
        return ConversationHandler.END
