from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from dataclasses import dataclass
from TelegramBot.DatabaseHandler import GetAulette

# Gli stati della conversazione
NOME_COMPLETO, SALDO, NOTIFICA = range(3)

# Creiamo una struct in modo tale da potere memorizzare tutte le informazioni 
# in base ad una chiave (id Telegram dello scrittore)
@dataclass
class User:
    Nome: str
    Saldo: float
    Notifica: int

# Inizializziamo il dizionario
usersAndValues = {}

# Chiediamo all'utente di Inserire il tag del nuovo utente
async def AddUser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Inserisci il nome completo dell'utente: ")
    
    usersAndValues[update.message.chat_id] = User("", 0, 0)

    return NOME_COMPLETO # Ritorniamo lo stato ID_TELEGRAM per andare in quella funzione

# Memorizziamo il messaggio mandato dall'utente come nome completo e chiediamo il saldo
async def InsertNomeCompleto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    usersAndValues[update.message.chat_id].Nome = update.message.text

    await update.message.reply_text(f"Ora inserisci il saldo inziale dell'utente:")
    return SALDO

# Memorizziamo il messaggio mandato dall'utente come saldo
async def InsertSaldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    saldo = update.message.text

    # Ma solo se è un numero, altrimenti ripeti
    if(not saldo.isdigit()):
        await update.message.reply_text(f"{update.message.text} non è un numero, riprova!")
        return SALDO

    saldo = float(saldo)
    usersAndValues[update.message.chat_id].Saldo = saldo

    await update.message.reply_text(f"Ottimo, l'utente {usersAndValues[update.message.chat_id].Nome}, verrà memorizzato con saldo pari a: {usersAndValues[update.message.chat_id].Saldo}€")
    return ConversationHandler.END

# Memorizziamo il messaggio mandato dall'utente come saldo
async def InsertNotifica(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = GetAulette()
    for row in rows:
        await update.message.reply_text(f"{row}")

    await update.message.reply_text(f"Ottimo, l'utente {usersAndValues[update.message.chat_id].Nome}, verrà memorizzato con saldo pari a: {usersAndValues[update.message.chat_id].Saldo}€")
    return ConversationHandler.END

# TODO: MANDARE RICHIESTA AL DB ED UNA VOLTA ENTRATO RIMUOVERE L'UTENTE DAL DIZIONARIO

def CreateAddUserHandler(Cancel):
    return ConversationHandler(
        entry_points=[CommandHandler('add', AddUser)],
        states={
            # Dipende dallo stato nella quale ci troviamo, richiama una funzione specifica
            NOME_COMPLETO: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertNomeCompleto)],
            SALDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertSaldo)]
        },
        fallbacks=[CommandHandler('cancel', Cancel)] # Possiamo annullare il comando corrente utilizzando /cancel
    )