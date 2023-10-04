from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from dataclasses import dataclass
from Modules.DatabaseHandler import GetAulette, CheckUserExists, GetAuletta, InsertUser
import re # Importiamo le RegEx
import os

# Gli stati della conversazione
NOME_COMPLETO, NOTIFICA = range(2)

# Creiamo una struct in modo tale da potere memorizzare tutte le informazioni 
# in base ad una chiave (id Telegram dello scrittore)
@dataclass
class User:
    Nome: str
    Auletta: int

# Inizializziamo il dizionario
usersAndValues = {}

async def AddUser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ADD_USER: Funzione iniziale per inserire un utente nel DB"""

    if(CheckUserExists(idTelegram=update.effective_chat.id)):
        # Se l'utente esiste, manda un messaggio e chiude il comando
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hai già un account! Ti sei dimenticato l'username? Fai /info")
        return ConversationHandler.END

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Inserisci il tuo nominativo in formato nome.cognome: ")

    usersAndValues[update.message.chat_id] = User("", 0)

    return NOME_COMPLETO # Ritorniamo lo stato ID_TELEGRAM per andare in quella funzione

async def InsertNomeCompleto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ADD_USER: Memorizziamo il messaggio mandato dall'utente come nome completo e chiediamo l'auletta di riferimento"""
    
    usernamePattern = "^[A-Z][a-zA-Z]*\.[A-Z][a-zA-Z]*(\d{2})?$" # Espressione regolare che controlla se il formato dell'username è nome.cognome00
    username = update.message.text

    # Controlliamo se il formato è giusto
    if not re.match(usernamePattern, username): # Se non appatta allora dai errore e richiedi
        await context.bot.send_message(chat_id=update.effective_chat.id, text="L'username non è nel formato UniPa 'nome.cognome00'. Iniziali grandi.")
        return NOME_COMPLETO

    modulePath = os.path.dirname(os.path.abspath(__file__)) # Otteniamo il percorso di questo file
    filePath = os.path.join(modulePath, '..', 'Resources', "ParoleVolgari.txt") # Directory delle cose "Parole Volgari"

    print(filePath)

    # Leggi il file delle parole volgari e crea un set di parole
    with open(filePath, 'r') as file:
        paroleVolgari = set(line.strip() for line in file)

        # Controlla se una delle parole volgari è contenuta nell'username
        if any(parola in username.upper() for parola in paroleVolgari):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="L'username contiene parole volgari. Riprova.")
            return NOME_COMPLETO

    usersAndValues[update.message.chat_id].Nome = username # Salviamo l'username

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

    return ConversationHandler.END

async def InsertUserButton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:    
    """ADD_USER: Quando l'utente seleziona un bottone chiama questo metodo"""
    query = update.callback_query
    
    await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")

    usersAndValues[update.effective_chat.id].Auletta = query.data

    username = usersAndValues[update.effective_chat.id].Nome
    nomeAuletta : str = GetAuletta(query.data)

    InsertUser(idTelegram=update.effective_chat.id, username=username)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ottimo, l'utente {usersAndValues[update.effective_chat.id].Nome} farà riferimento all'auletta {nomeAuletta}")

# TODO: MANDARE RICHIESTA INSERT AL DB ED UNA VOLTA ENTRATO RIMUOVERE L'UTENTE DAL DIZIONARIO
# TODO: IL BOT SI BLOCCA FINO A QUANDO NON GLI ARRIVA CANCEL ALLA FINE DELL'INSERIMENTO, DOPO AVER AMMACCATO UN BOTTONE

def CreateAddUserHandler(Cancel):
    """ADD_USER: Handler Della funzione ADD_USER"""
    
    return ConversationHandler(
        entry_points=[CommandHandler('add', AddUser)],
        states={
            # Dipende dallo stato nella quale ci troviamo, richiama una funzione specifica
            NOME_COMPLETO: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertNomeCompleto)]
        },
        fallbacks=[CommandHandler('cancel', Cancel)] # Possiamo annullare il comando corrente utilizzando /cancel
    )