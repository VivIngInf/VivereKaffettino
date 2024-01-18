# IMPORTANTE: INSTALLARE PIGAR USANDO "pip install pigar"
# SE AGGIUNGETE LIBRERIE, ESEGUITE IL COMANDO "pigar generate"
# QUESTO COMANDO SERVE A CREARE UN FILE CHE SPECIFICA TUTTE LE LIBRERIE
# DA INSTALLARE SU UNA MACCHINA FRESCA

# region Imports

import atexit # Libreria che ci permette di creare un metodo per quando il codice viene interrotto

# Librerie Telegram
import logging
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters

# File complementari, ho preferito spezzettare questi codici nei propri file per evitare di fare
# un porcile nel file main
from Modules.Bot.ShowBalance import ShowBalance
from Modules.Bot.UserInfo import Info
from Modules.Shared.Configs import LoadConfigs, GetToken
from Modules.Bot.SetAdmin import CreateSetAdminHandler, CreateUnsetAdminHandler
from Modules.Bot.Nostalgia import Nostalgia
from Modules.Bot.Start import Start
from Modules.Bot.End import End
from Modules.Bot.Stop import Stop
from Modules.Bot.AddUser import registration_conv, start_registration
from Modules.Bot.Register import *
from Modules.Bot.Resoconto import SendResoconto

from Modules.Bot.States import *

import datetime
import time

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Bisogna installare openpyxl, pandas e python-telegram-bot[job-queue]

# endregion

# Configurazione di logging base
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    LoadConfigs()
    application = Application.builder().token(GetToken()).build()

    # Set up top level ConversationHandler (selecting action)
    # Because the states of the third level conversation map to the ones of the second level
    # conversation, we need to make sure the top level conversation can also handle them
    selection_handlers = [
        CallbackQueryHandler(ShowBalance, pattern="^" + str(SHOWING) + "$"),
        CallbackQueryHandler(Info, pattern="^" + str(INFO) + "$"),
        CallbackQueryHandler(Register, pattern="^" + str(REGISTER) + "$"),
        CallbackQueryHandler(End, pattern="^" + str(END) + "$"),
    ]

    # DANIELE: ENTRYPOINT BOT

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", Start)],
        states={
            MAINMENU: [CallbackQueryHandler(Start, pattern="^" + str(END) + "$")],
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            REGISTER: [registerConv],
            STOPPING: [CommandHandler("start", Start)],
        },
        fallbacks=[CommandHandler("stop", Stop)],
    )

    application.add_handler(conv_handler)

    job_queue = application.job_queue
    job_queue.run_daily(SendResoconto, time=datetime.time(hour=3, minute=39, second=0, tzinfo=pytz.timezone('Europe/Rome')))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()