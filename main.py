import os
from dotenv import load_dotenv, find_dotenv

# Librerie Telegram
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Configurazione di logging base
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Creiamo la funzione start che se richiamata stampa a video "BUONGIORNISSIMO, KAFFÈ!?"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="BUONGIORNISSIMO, KAFFÈ!?")

if __name__ == "__main__":
    load_dotenv(find_dotenv()) # Carichiamo il file di ambiente dove è salvato il token
    application = ApplicationBuilder().token(os.environ.get("BOT_TOKEN")).build() # Ci impossessiamo del bot con il nostro TOKEN
    
    # Creiamo il comando start e lo aggiungiamo ai comandi runnabili
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    application.run_polling() # Inizializza l'app
    