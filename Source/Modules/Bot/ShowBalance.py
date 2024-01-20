from telegram import Update
from telegram.ext import ContextTypes
from ..Shared.Query import GetBalance, GetIsVerified
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..Bot.States import *

async def ShowBalance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """SHOW_BALANCE: Manda come messaggio all'utente il suo saldo a partire dall'ID_Telegram"""

    user_data = context.user_data

    idTelegram = str(update.effective_chat.id)

    saldo = GetBalance(idTelegram) # Chiamata al DB per ottenere il saldo a partire dall'ID_Telegram
    text = f"Il tuo saldo è pari ad: {saldo}€"

    buttons = [[InlineKeyboardButton(text="Back", callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    user_data[START_OVER] = True

    return MAINMENU