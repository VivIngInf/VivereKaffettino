from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

INSERT_BALANCE, UPDATE_BALANCE = range(2)

"""async def UpdateBalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    UPDATE_BALANCE: 

    saldo = update.message.text

    # Ma solo se è un numero, altrimenti ripeti
    if(not saldo.isdigit()):
        await update.message.reply_text(f"{update.message.text} non è un numero, riprova!")
        return SALDO

    saldo = float(saldo)

    return NOTIFICA"""