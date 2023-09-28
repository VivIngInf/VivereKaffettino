from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from TelegramBot.DatabaseHandler import GetBalance

NOME_COMPLETO = range(1)

# Creiamo la funzione Cancel che ci permette di uscire dalle conversazioni
async def ShowBalance(update: Update, context: ContextTypes.DEFAULT_TYPE):

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