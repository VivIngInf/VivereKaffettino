from telegram import Update
from telegram.ext import ContextTypes
from Modules.Bot.States import *
from Modules.Bot.Start import Start

def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return Start(update, context)
