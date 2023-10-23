from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from dataclasses import dataclass
from ..Shared.Query import GetAulette, CheckUserExists, GetAuletta, InsertUser, CheckUsernameExists
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

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Inserisci il tuo nominativo in formato Nome.Cognome: ")

    usersAndValues[update.message.chat_id] = User("", 0)

    return NOME_COMPLETO # Ritorniamo lo stato ID_TELEGRAM per andare in quella funzione

async def InsertNomeCompleto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ADD_USER: Memorizziamo il messaggio mandato dall'utente come nome completo e chiediamo l'auletta di riferimento"""
    
    usernamePattern = "^[A-Z][a-zA-Z]*\.[A-Z][a-zA-Z]*(\d{2})?$" # Espressione regolare che controlla se il formato dell'username è nome.cognome00
    username = update.message.text

    # Controlliamo se il formato è giusto
    if not re.match(usernamePattern, username): # Se non appatta allora dai errore e richiedi
        await context.bot.send_message(chat_id=update.effective_chat.id, text="L'username non è nel formato UniPa 'Nome.Cognome00'. Iniziali grandi.")
        return NOME_COMPLETO

    modulePath = os.path.dirname(os.path.abspath(__file__)) # Otteniamo il percorso di questo file
    filePath = os.path.join(modulePath, '..', 'Resources', "ParoleVolgari.txt") # Directory delle cose "Parole Volgari"

    print(filePath)

    # Leggi il file delle parole volgari e crea un set di parole
    with open(filePath, 'r') as file:
        paroleVolgari = set(line.strip() for line in file)

        # Controlla se una delle parole volgari è contenuta nell'username
        if any(parola in username.upper() for parola in paroleVolgari):
            return NOME_COMPLETO

    # Controllare se esiste già lo stesso username
    if CheckUsernameExists(username=username):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Questo username esiste già, riprova.")
        return NOME_COMPLETO

    usersAndValues[update.message.chat_id].Nome = username # Salviamo l'username

    # Facciamo una chiamata al DB per prendere le varie aulette
    rows = GetAulette()

    keyboard = []
    
    # Mettiamo le aulette in riga
    for row in rows:
        button = InlineKeyboardButton(text=row[1], callback_data="Auletta:"+row[0])
        keyboard.append([button])
        
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Mandiamo il messaggio con la tastiera per poter scegliere l'auletta di riferimento
    await update.message.reply_text(f"Ora seleziona in quale auletta vuoi prendere la carta:", reply_markup=reply_markup)

    return ConversationHandler.END

async def AddUserKeyboardHandler(update: Update, context: ContextTypes.DEFAULT_TYPE, idAuletta: int) -> None:
    usersAndValues[update.effective_chat.id].Auletta = idAuletta

    username = usersAndValues[update.effective_chat.id].Nome
    nomeAuletta : str = GetAuletta(idAuletta=idAuletta)

    InsertUser(idTelegram=update.effective_chat.id, username=username)

    usersAndValues.pop([update.effective_chat.id])

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ottimo, l'utente {usersAndValues[update.effective_chat.id].Nome} farà riferimento all'auletta {nomeAuletta}")


async def CreateAddUserHandler(Cancel):
    """ADD_USER: Handler Della funzione ADD_USER"""
    
    return ConversationHandler(
        entry_points=[CommandHandler('add', AddUser)],
        states={
            # Dipende dallo stato nella quale ci troviamo, richiama una funzione specifica
            NOME_COMPLETO: [MessageHandler(filters.TEXT & ~filters.COMMAND, InsertNomeCompleto)]
        },
        fallbacks=[CommandHandler('cancel', Cancel)] # Possiamo annullare il comando corrente utilizzando /cancel
    )