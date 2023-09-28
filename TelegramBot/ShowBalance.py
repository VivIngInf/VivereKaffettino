from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler
from TelegramBot.DatabaseHandler import GetBalance

async def ShowBalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SHOW_BALANCE: Manda come messaggio all'utente il suo saldo a partire dall'ID_Telegram"""

    idTelegram = str(update.effective_chat.id)
    saldo = GetBalance(idTelegram)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Il tuo saldo è pari ad: {saldo}")
    return ConversationHandler.END


def CreateShowBalanceHandler(Cancel):
    """SHOW_BALANCE: Handler Della funzione SHOW_BALANCE"""
    
    return ConversationHandler(
        entry_points=[CommandHandler('saldo', ShowBalance)],
        states={},
        fallbacks=[CommandHandler('cancel', Cancel)] # Possiamo annullare il comando corrente utilizzando /cancel
    )