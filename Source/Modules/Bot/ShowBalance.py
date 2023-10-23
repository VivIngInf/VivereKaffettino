from telegram import Update
from telegram.ext import ContextTypes
from ..Shared.Query import GetBalance, GetIsVerified

async def ShowBalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SHOW_BALANCE: Manda come messaggio all'utente il suo saldo a partire dall'ID_Telegram"""

    idTelegram = str(update.effective_chat.id)

    # Se l'utente non è verificato allora ignora il comando
    if (not GetIsVerified(idTelegram=idTelegram)):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Il tuo account ancora non è stato verificato.\n Hai già avuto la tua carta? Se si contatta chi te l'ha data.")

    saldo = GetBalance(idTelegram) # Chiamata al DB per ottenere il saldo a partire dall'ID_Telegram
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Il tuo saldo è pari ad: {saldo}")
