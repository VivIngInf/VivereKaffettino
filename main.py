# IMPORTANTE: INSTALLARE PIGAR USANDO "pip install pigar"
# SE AGGIUNGETE LIBRERIE, ESEGUITE IL COMANDO "pigar generate"
# QUESTO COMANDO SERVE A CREARE UN FILE CHE SPECIFICA TUTTE LE LIBRERIE
# DA INSTALLARE SU UNA MACCHINA FRESCA

import atexit # Libreria che ci permette di creare un metodo per quando il codice viene interrotto

# Librerie Telegram
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler

# File complementari, ho preferito spezzettare questi codici nei propri file per evitare di fare
# un porcile nel file main
from TelegramBot.InsertUser import CreateAddUserHandler, InsertUserButton
from TelegramBot.ShowBalance import CreateShowBalanceHandler

from TelegramBot.LoadConfig import GetToken

# Configurazione di logging base
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Creiamo la funzione start che se richiamata stampa a video "BUONGIORNISSIMO, KAFFÈ!?"
async def Start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="BUONGIORNISSIMO, KAFFÈ!?")

# Creiamo la funzione Cancel che ci permette di uscire dalle conversazioni
async def Cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Arrivederci!")
    return ConversationHandler.END

if __name__ == "__main__":

    application = ApplicationBuilder().token(token=GetToken()).build() # Ci impossessiamo del bot con il nostro TOKEN

    # Creiamo il comando start e lo aggiungiamo ai comandi runnabili
    start_handler = CommandHandler('start', Start)
    application.add_handler(start_handler)

    # Creiamo il comando AddUser e lo aggiungiamo ai comandi runnabili
    # N.B: CreateAddUserHandler è un comando esterno presente in InsertUser.py
    addUser_handler = CreateAddUserHandler(Cancel=Cancel)
    application.add_handler(addUser_handler)

    showBalance_handler = CreateShowBalanceHandler(Cancel=Cancel)
    application.add_handler(showBalance_handler)

    # Handler della keyboard per l'auletta
    application.add_handler(CallbackQueryHandler(InsertUserButton))

    application.run_polling() # Inizializza l'app    
    