from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

# Gli stati della conversazione
ID_TELEGRAM, NOME_COMPLETO, SALDO = range(3)

# I valori che vogliamo memorizzare
idTelegram = ""
nomeCompleto = ""
saldo = 0

# Chiediamo all'utente di Inserire il tag del nuovo utente
async def AddUser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Inserisci il tag dell'utente: ")
    return ID_TELEGRAM # Ritorniamo lo stato ID_TELEGRAM per andare in quella funzione

# Memorizziamo il messaggio mandato dall'utente come username e chiediamo il nome completo
async def InsertIDTelegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global idTelegram
    idTelegram = update.message.text
    
    await update.message.reply_text(f"Ora inserisci il nome completo dell'utente:")
    return NOME_COMPLETO

# Memorizziamo il messaggio mandato dall'utente come nomecompleto e chiediamo il saldo
async def InsertNomeCompleto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global nomeCompleto
    nomeCompleto = update.message.text

    await update.message.reply_text(f"Ora inserisci il saldo iniziale di {nomeCompleto}:")
    return SALDO

# Memorizziamo il messaggio mandato dall'utente come saldo
async def InsertSaldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global saldo
    saldo = update.message.text

    # Ma solo se è un numero, altrimenti ripeti
    if(saldo.isdigit()):
        await update.message.reply_text(f"{update.message.text} non è un numero, riprova!")
        return SALDO

    saldo = float(saldo)

    await update.message.reply_text(f"Ottimo, l'utente {nomeCompleto} con ID: {idTelegram}, verrà memorizzato con saldo pari a: {saldo}€")
    return ConversationHandler.END

def CreateAddUserHandler(Cancel):
    return ConversationHandler(
        entry_points=[CommandHandler('add', AddUser)],
        states={
            # Dipende dallo stato nella quale ci troviamo, richiama una funzione specifica
            ID_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertIDTelegram)],
            NOME_COMPLETO: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertNomeCompleto)],
            SALDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertSaldo)]
        },
        fallbacks=[CommandHandler('cancel', Cancel)] # Possiamo annullare il comando corrente utilizzando /cancel
    )