# IMPORTANTE: INSTALLARE PIGAR USANDO "pip install pigar"
# SE AGGIUNGETE LIBRERIE, ESEGUITE IL COMANDO "pigar generate"
# QUESTO COMANDO SERVE A CREARE UN FILE CHE SPECIFICA TUTTE LE LIBRERIE
# DA INSTALLARE SU UNA MACCHINA FRESCA

# region Imports

import atexit  # Libreria che ci permette di creare un metodo per quando il codice viene interrotto

# Librerie Telegram
import logging
import pytz
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, \
    MessageHandler, filters

# File complementari, ho preferito spezzettare questi codici nei propri file per evitare di fare
# un porcile nel file main (hai fatto bene bro)
from Modules.Bot.ShowBalance import ShowBalance
from Modules.Bot.UserInfo import Info
from Modules.Shared.Configs import LoadConfigs, GetToken
from Modules.Bot.Nostalgia import Nostalgia
from Modules.Bot.Start import Start
from Modules.Bot.Stop import Stop_command
from Modules.Bot.Resoconti import SendDailyResoconto, SendUsersResoconto
from Modules.Bot.NavMenu import handle_messages, button_callbacks
from Modules.Bot.BirthdayList import FlushBirthdayList
from Modules.Bot.Utility import *

from Modules.Shared.Query import GetUnverifiedUsers

import datetime
import time

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters
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

    application.add_handler(CommandHandler("start", Start))
    application.add_handler(CommandHandler("stop", Stop_command))
    # Tengo traccia di ogni messaggio e bottone premuto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    application.add_handler(CallbackQueryHandler(button_callbacks))

    job_queue = application.job_queue
    job_queue.run_daily(SendDailyResoconto,
                        time=datetime.time(hour=23, minute=55, second=0, tzinfo=pytz.timezone('Europe/Rome')))
    job_queue.run_daily(FlushBirthdayList, time=datetime.time(hour=23, minute=59, second=0, tzinfo=pytz.timezone('Europe/Rome')))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
