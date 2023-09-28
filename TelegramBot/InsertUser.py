from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

async def AddUser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ADD_USER: Funzione iniziale per inserire un utente nel DB"""

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Inserisci il nome completo dell'utente: ")
    
    usersAndValues[update.message.chat_id] = User("", 0, 0)

    return NOME_COMPLETO # Ritorniamo lo stato ID_TELEGRAM per andare in quella funzione

async def InsertNomeCompleto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ADD_USER: Memorizziamo il messaggio mandato dall'utente come nome completo e chiediamo il saldo"""
    
    usersAndValues[update.message.chat_id].Nome = update.message.text

    await update.message.reply_text(f"Ora inserisci il saldo inziale dell'utente:")
    return SALDO

async def InsertSaldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ADD_USER: Memorizziamo il messaggio mandato dall'utente come saldo e prepariamo la keyboard per chiedere l'auletta"""

    saldo = update.message.text

    # Ma solo se è un numero, altrimenti ripeti
    if(not saldo.isdigit()):
        await update.message.reply_text(f"{update.message.text} non è un numero, riprova!")
        return SALDO

    saldo = float(saldo)
    usersAndValues[update.message.chat_id].Saldo = saldo

    # Facciamo una chiamata al DB per prendere le varie aulette
    rows = GetAulette()

    keyboard = []
    
    # Mettiamo le aulette in riga
    for row in rows:
        button = InlineKeyboardButton(text=row[1], callback_data=row[0])
        keyboard.append([button])
        
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Mandiamo il messaggio con la tastiera per poter scegliere l'auletta di riferimento
    await update.message.reply_text(f"Ora seleziona in quale auletta vuoi prendere la carta:", reply_markup=reply_markup)

    return NOTIFICA

async def InsertNotifica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ADD_USER: Memorizziamo l'auletta e mostriamo il risultato finale"""

    await update.message.reply_text(f"Ottimo, l'utente {usersAndValues[update.message.chat_id].Nome}, verrà memorizzato con saldo pari a: {usersAndValues[update.message.chat_id].Saldo}€")
    return ConversationHandler.END

async def InsertUserButton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:    
    """ADD_USER: Quando l'utente seleziona un bottone chiama questo metodo"""
    query = update.callback_query
    
    await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")
    return ConversationHandler.END

# TODO: MANDARE RICHIESTA AL DB ED UNA VOLTA ENTRATO RIMUOVERE L'UTENTE DAL DIZIONARIO
# TODO: IL BOT SI BLOCCA FINO A QUANDO NON GLI ARRIVA CANCEL ALLA FINE DELL'INSERIMENTO, DOPO AVER AMMACCATO UN BOTTONE

def CreateAddUserHandler(Cancel):
    """ADD_USER: Handler Della funzione ADD_USER"""
    
    return ConversationHandler(
        entry_points=[CommandHandler('add', AddUser)],
        states={
            # Dipende dallo stato nella quale ci troviamo, richiama una funzione specifica
            NOME_COMPLETO: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertNomeCompleto)],
            SALDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertSaldo)],
            NOTIFICA: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertNotifica)]
        },
        fallbacks=[CommandHandler('cancel', Cancel)] # Possiamo annullare il comando corrente utilizzando /cancel
    )