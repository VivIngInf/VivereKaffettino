from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import InputFile
import random
import os

async def Nostalgia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """NOSTALGIA: Fa diventare nostalgici tutti quanti"""

    modulePath = os.path.dirname(os.path.abspath(__file__)) # Otteniamo il percorso di questo file
    dirPath = os.path.join(modulePath, '..', 'Resources', 'Nostalgia') # Directory delle cose "nostalgiche"
    files = [f for f in os.listdir(dirPath) if (os.path.join(dirPath, f))] # Prendiamo i file nella dir

    randomFile = random.choice(files)
    filePath = os.path.join(dirPath, randomFile)

    if(not filePath.endswith(".mp4")):
        with open(filePath, 'rb') as imageFile:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(imageFile))
    else:
        with open(filePath, 'rb') as videoFile:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=InputFile(videoFile))

    return None