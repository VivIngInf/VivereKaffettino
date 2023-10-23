# IMPORTANTE: INSTALLARE PIGAR USANDO "pip install pigar"
# SE AGGIUNGETE LIBRERIE, ESEGUITE IL COMANDO "pigar generate"
# QUESTO COMANDO SERVE A CREARE UN FILE CHE SPECIFICA TUTTE LE LIBRERIE
# DA INSTALLARE SU UNA MACCHINA FRESCA

import atexit # Libreria che ci permette di creare un metodo per quando il codice viene interrotto

# Librerie Telegram
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters

# File complementari, ho preferito spezzettare questi codici nei propri file per evitare di fare
# un porcile nel file main
from Modules.Bot.AddUser import CreateAddUserHandler
from Modules.Bot.ShowBalance import ShowBalance
from Modules.Bot.UserInfo import Info
from Modules.Shared.Configs import LoadConfigs, GetToken
from Modules.Bot.SetAdmin import CreateSetAdminHandler, CreateUnsetAdminHandler
from Modules.Bot.Nostalgia import Nostalgia
from Modules.Bot.Start import Start
from Modules.Bot.KeyboardsHandler import KeyBoardHandler

from telegram import BotCommand, Bot

# Configurazione di logging base
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

MAIN_MENU, USER, ADMIN = range(3)

# Creiamo la funzione Cancel che ci permette di uscire dalle conversazioni
async def Cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Arrivederci!")
    return ConversationHandler.END

async def SetCommands() -> None:
    
    bot = application.updater.bot

    commands = [
        BotCommand("start", "un bellissimo risveglio"),
        BotCommand("saldo", "Visualizza il saldo rimanente sul tuo conto"),
        BotCommand("info", "Visualizza l'ID Telegram ed il tuo username"),
        BotCommand("add", "Ti permette di registrarti se non hai già un account"),
    ]

    await bot.setMyCommands(commands)
    
    return None

# TODO: IMPLEMENTARE CHE TUTTI I COMANDI AD ESCLUSIONE DI INFO, ADD E KAMERATA KAFFETTINO DEBBANO AVERE L'UTENTE

if __name__ == "__main__":

    LoadConfigs()
    application = ApplicationBuilder().token(token=GetToken()).build() # Ci impossessiamo del bot con il nostro TOKEN

    # Creiamo il comando start e lo aggiungiamo ai comandi runnabili
    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', Start)],
        states={
        },
        fallbacks=[CommandHandler('cancel', Cancel)]
    )

    application.add_handler(start_handler)

    # Handler delle keyboards
    application.add_handler(CallbackQueryHandler(KeyBoardHandler))

    """# Creiamo il comando AddUser e lo aggiungiamo ai comandi runnabili
    # N.B: CreateAddUserHandler è un comando esterno presente in InsertUser.py
    addUser_handler = CreateAddUserHandler(Cancel=Cancel)
    application.add_handler(addUser_handler)

    showBalance_handler = CommandHandler('saldo', ShowBalance)
    application.add_handler(showBalance_handler)

    # Handler info
    info_handler = CommandHandler('info', Info)
    application.add_handler(info_handler)

    # Creiamo il comando AddAdmin e lo aggiungiamo ai comandi runnabili
    setAdmin_handler = CreateSetAdminHandler(Cancel=Cancel)
    application.add_handler(setAdmin_handler)

    # Creiamo il comando AddAdmin e lo aggiungiamo ai comandi runnabili
    unsetAdmin_handler = CreateUnsetAdminHandler(Cancel=Cancel)
    application.add_handler(unsetAdmin_handler)

    # Creiamo il comando kamerataKaffettino e lo aggiungiamo ai comandi runnabili
    kamerata_handler = CommandHandler('kamerataKaffettino', Nostalgia)
    application.add_handler(kamerata_handler)

    SetCommands()"""

    application.run_polling() # Inizializza l'app    
    