from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from Modules.DatabaseHandler import GetIdTelegram, SetAdminDB, CheckUserExists, GetIsAdmin

USERNAME = range(1)

async def SetAdmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SET_ADMIN:  Questa funzione deve permettere ad un amministratore
    di inserire l'username di un utente e renderlo amministratore"""

    # Controlliamo se amministratore
    if not GetIsAdmin(idTelegram=update.effective_chat.id):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Non hai i permessi per eseguire questo comando")
        return ConversationHandler.END

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Inserisci l'username dell'utente da promuovere:")

    return USERNAME

async def InsertUsernamePromote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SET_ADMIN:  Questa funzione deve controllare se l'utente inserito dall'amministratore esiste
    ed in caso aggiornare il suo stato in IS_ADMIN = 1"""

    username : str = update.message.text
    idTelegram = GetIdTelegram(username=username)
    
    if(not CheckUserExists(idTelegram=idTelegram)):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Non esiste un utente con username: {username}\nRiprova oppure fai \cancel")
        return USERNAME

    SetAdminDB(idTelegram=idTelegram, state=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Cambiati i permessi di {username}.\nAdesso è: Amministratore!")


    return ConversationHandler.END

async def InsertUsernameDemote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SET_ADMIN:  Questa funzione deve controllare se l'utente inserito dall'amministratore esiste
    ed in caso aggiornare il suo stato in IS_ADMIN = 0"""

    username : str = update.message.text
    idTelegram = GetIdTelegram(username=username)
    
    if(not CheckUserExists(idTelegram=idTelegram)):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Non esiste un utente con username: {username}\nRiprova oppure fai \cancel")
        return USERNAME

    SetAdminDB(idTelegram=idTelegram, state=False)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Cambiati i permessi di {username}.\nAdesso è: Utente!")

    return ConversationHandler.END

def CreateSetAdminHandler(Cancel):
    return ConversationHandler(
        entry_points=[CommandHandler('promote', SetAdmin)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertUsernamePromote)]
        },
        fallbacks=[CommandHandler('cancel', Cancel)] # Possiamo annullare il comando corrente utilizzando /cancel
    )

def CreateUnsetAdminHandler(Cancel):
    return ConversationHandler(
        entry_points=[CommandHandler('demote', SetAdmin)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertUsernameDemote)]
        },
        fallbacks=[CommandHandler('cancel', Cancel)] # Possiamo annullare il comando corrente utilizzando /cancel
    )