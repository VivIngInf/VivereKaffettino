from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ContextTypes
from ...Shared.Query import GetUsername, CheckUserExists, GetIsAdmin, GetIsVerified


async def Info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """USER_INFO: Permette all'utente di vedere il suo ID_Telegram ed il suo Username"""

    telegramID = update.effective_chat.id
    username = GetUsername(idTelegram=telegramID)
    isAdmin = GetIsAdmin(idTelegram=telegramID)
    isVerified = GetIsVerified(idTelegram=telegramID)

    state: str = "Verificato" if isVerified else "Richiesta in sospeso"

    role: str = "Amministratore" if isAdmin else "Utente"

    text = f"""<b>ID Telegram</b>: {telegramID}\n<b>Username</b>: {username}\n<b>Stato</b>: {state}\n<b>Ruolo</b>: {role}\n"""

    buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode=constants.ParseMode.HTML)
