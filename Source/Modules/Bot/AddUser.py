from telegram import Update, CallbackQuery,  InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler
from Modules.Bot.Utility import *
from Modules.Bot.Stop import Stop
from Modules.Bot.Start import Start
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Prompt user to input data for selected feature."""
    text = "Okay, tell me."
    button = InlineKeyboardButton(text="Aggiungi info", callback_data=str(SUCA))
    keyboard = InlineKeyboardMarkup.from_button(button)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return REGISTER  

async def InsertUsername(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Prompt user to input data for selected feature."""

    username : str = update.message.text

    await update.callback_query.edit_message_text(text=username)

    return ConversationHandler.END  

registration_conv =  ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                InsertUsername, pattern="^" + str(SUCA) + "$"
            )    
        ],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertUsername)]
        },
        fallbacks=[
            CommandHandler("stop", Stop),
        ],
        map_to_parent={
            # Return to second level menu
            END: SELECTING_LEVEL,
            # End conversation altogether
            STOPPING: STOPPING,
        },
    )