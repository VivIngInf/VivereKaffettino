from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler
from TelegramBot.DatabaseHandler import GetBalance

async def ShowBalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SHOW_BALANCE: Manda come messaggio all'utente il suo saldo a partire dall'ID_Telegram"""

    idTelegram = str(update.effective_chat.id)
    saldo = GetBalance(idTelegram) # Chiamata al DB per ottenere il saldo a partire dall'ID_Telegram

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Il tuo saldo è pari ad: {saldo}")