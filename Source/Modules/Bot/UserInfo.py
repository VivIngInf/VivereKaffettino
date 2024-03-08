from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..Shared.Query import GetUsername, CheckUserExists, GetIsAdmin, GetIsVerified
from Modules.Bot.States import *


async def Info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """USER_INFO: Permette all'utente di vedere il suo ID_Telegram ed il suo Username"""

    user_data = context.user_data

    telegramID = update.effective_chat.id
    username = GetUsername(idTelegram=telegramID)
    isAdmin = GetIsAdmin(idTelegram=telegramID)
    isVerified = GetIsVerified(idTelegram=telegramID)

    state: str = "Verificato" if isVerified else "Richiesta in sospeso"

    role: str = "Amministratore" if isAdmin else "Utente"

    text = f"""ID Telegram: {telegramID}\nUsername: {username}\nStato: {state}, Ruolo: {role}\n"""

    buttons = [[InlineKeyboardButton("Ritorna al menu principale", callback_data='back_main_menu')]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
