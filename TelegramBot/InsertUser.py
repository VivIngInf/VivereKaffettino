from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

# Add User States
ID_TELEGRAM, NOME_COMPLETO, SALDO = range(3)

# Inseriamo nel DB l'ID Utente ed il nome di un utente
async def AddUser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Inserisci l'username dell'utente: ")
    return ID_TELEGRAM

async def InsertIDTelegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idTelegram = update.message.text
    await update.message.reply_text(f"L'id inserito è: {idTelegram}")
    return ConversationHandler.END

def CreateAddUserHandler(Cancel):
    return ConversationHandler(
        entry_points=[CommandHandler('add', AddUser)],
        states={
            ID_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertIDTelegram)]
        },
        fallbacks=[CommandHandler('cancel', Cancel)]
    )