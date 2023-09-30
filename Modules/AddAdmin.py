from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from Modules.DatabaseHandler import GetIdTelegram, SetAdmin, CheckUserExists

USERNAME = range(1)

async def AddAdmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ADD_ADMIN:  Questa funzione deve permettere ad un amministratore
    di inserire l'username di un utente e renderlo amministratore"""

    # TODO: SOLO UN AMMINISTRATORE PUO' ESEGUIRE QUESTO COMANDO

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Inserisci l'username dell'utente da promuovere:")

    return USERNAME

async def InsertUsername(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ADD_ADMIN:  Questa funzione deve permettere ad un amministratore
    di inserire l'username di un utente e renderlo amministratore"""

    username : str = update.message.text
    idTelegram = GetIdTelegram(username=username)
    
    if(not CheckUserExists(idTelegram=idTelegram)):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Non esiste un utente con username: {username}\nRiprova oppure fai \cancel")
        return USERNAME

    SetAdmin(idTelegram=idTelegram)

    return ConversationHandler.END

def CreateAddAdminHandler(Cancel):
    return ConversationHandler(
        entry_points=[CommandHandler('promote', AddAdmin)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertUsername)]
        },
        fallbacks=[CommandHandler('cancel', Cancel)] # Possiamo annullare il comando corrente utilizzando /cancel
    )