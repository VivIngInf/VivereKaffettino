from telegram.ext import CallbackContext
from telegram import InputFile
from ..Shared.Query import GetDebitori
import random
import os

def getRandomImage() -> InputFile:
    # Ottieni il percorso completo della cartella selezionata
    modulePath = os.path.dirname(os.path.abspath(__file__)) # Otteniamo il percorso di questo file
    
    while os.path.basename(modulePath) != 'VivereKaffettino':
        modulePath = os.path.dirname(modulePath)

    folder_path = os.path.join(modulePath, "Resources", "Images", "Debt")

    # Ottieni la lista dei file nella cartella selezionata
    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Seleziona casualmente un'immagine dalla cartella selezionata
    random_image = random.choice(image_files)

    # Costruisci il percorso completo del file selezionato
    image_path = os.path.join(folder_path, random_image)

    # Invia l'immagine all'utente
    return open(image_path, 'rb')


async def SendMessageToDebtors(context: CallbackContext) -> None:
    debitori : list = GetDebitori()

    for username, id_telegram, debito in debitori:
        await context.bot.send_photo(chat_id=id_telegram, photo=getRandomImage(), caption=str(f"Ciao {username}! Ti ricordiamo che devi ancora estinguere il tuo debito di: {debito * -1}€.\nPer favore, estinguilo al più presto, grazie!"))

