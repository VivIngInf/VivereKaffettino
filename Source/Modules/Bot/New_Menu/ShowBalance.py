from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...Shared.Query import GetBalance, GetUsername


async def ShowBalance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """SHOW_BALANCE: Manda come messaggio all'utente il suo saldo a partire dall'ID_Telegram"""

    user_data = context.user_data

    idTelegram = str(update.effective_chat.id)

    saldo = GetBalance(idTelegram)  # Chiamata al DB per ottenere il saldo a partire dall'ID_Telegram
    text = f"{GetUsername(idTelegram)}, il tuo saldo è pari ad: {saldo}€"

    buttons = [[InlineKeyboardButton("Ritorna al menu principale", callback_data='back_main_menu')]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
