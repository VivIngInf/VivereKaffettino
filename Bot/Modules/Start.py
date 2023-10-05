import os
import random
from datetime import datetime
from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler
from Modules.DatabaseHandler import GetIsAdmin, CheckUserExists, GetIsVerified, GetUsername

def GiornoCorrente() -> str:
    """Funzione per ottenere il giorno della settimana attuale come stringa"""
    
    weekdays : list = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    return weekdays[datetime.now().weekday()]

def GiornoFestivo():
    """ Funzione per verificare se la data attuale è una festività specifica"""
    
    current_date = datetime.now()
    pasqua : datetime = calcola_pasqua(datetime.now().year)
    
    festive_dates = [
        (12, 13),  # Santa Lucia (13 dicembre)
        (12, 24),  # Vigilia Natale (24 dicembre)
        (12, 25),  # Natale (25 dicembre)
        (pasqua.month, pasqua.day), # Pasqua
        (pasqua.month, pasqua.day + 1) # Pasquetta 
        # Aggiungi altre festività qui
    ]
    
    return (current_date.month, current_date.day) in festive_dates

def calcola_pasqua(anno) -> datetime:
    """'Sta funzione l'ha fatta chatGPT, non mi volevo studiare come funzionasse l'algoritmo kekw"""

    a = anno % 19
    b = anno // 100
    c = anno % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451

    # Creare un oggetto datetime anziché chiamare datetime.date()
    data_pasqua = datetime(anno, (h + l - 7 * m + 114) // 31, ((h + l - 7 * m + 114) % 31) + 1)

    return data_pasqua


def SendRandomImage() -> InputFile:
    """'Sta funzione l'ha fatta chatGPT, non mi volevo studiare come funzionasse l'algoritmo kekw"""

    # Determina la data attuale
    current_date = datetime.now()

    # Elenco delle possibili cartelle in cui cercare le immagini
    possible_folders = []

    # Verifica se è dicembre
    if current_date.month == 12:
        possible_folders.append('Natale')

    # Verifica se è Pasqua o Pasquetta
    pasqua_date = calcola_pasqua(current_date.year)

    if (current_date.month, current_date.day) == (pasqua_date.month, pasqua_date.day):
        possible_folders.append('Pasqua')
    elif (current_date.month, current_date.day) == (pasqua_date.month, pasqua_date.day + 1):
        possible_folders.append('Pasquetta')

    # Verifica se è Santa Lucia
    if (current_date.month, current_date.day) == (12, 13):
        possible_folders.append('Santa Lucia')

    # Se non è un giorno festivo, aggiungi 'generiche' e la cartella specifica del giorno della settimana
    if not possible_folders:
        possible_folders.extend(['Generiche', GiornoCorrente()])

    # Seleziona casualmente una cartella tra quelle possibili
    selected_folder = random.choice(possible_folders)

    # Ottieni il percorso completo della cartella selezionata
    modulePath = os.path.dirname(os.path.abspath(__file__)) # Otteniamo il percorso di questo file
    folder_path = os.path.join(modulePath, "..", "Resources", "Images", selected_folder)
 
    # Ottieni la lista dei file nella cartella selezionata
    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    if image_files:
        # Seleziona casualmente un'immagine dalla cartella selezionata
        random_image = random.choice(image_files)

        # Costruisci il percorso completo del file selezionato
        image_path = os.path.join(folder_path, random_image)

        # Invia l'immagine all'utente
        return open(image_path, 'rb')

async def Start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    image : InputFile = SendRandomImage()

    risposta = ""
    mainMenuKeyboard = []

    if(not CheckUserExists(idTelegram=update.effective_chat.id)): # Non sei ancora registrato
        risposta = """Hey, è la prima volta che visiti vivere kaffetino?
        Registrati premendo il bottone sottostante!"""
        
        register = InlineKeyboardButton(text="📝 REGISTRATI 📝", callback_data="REG")

        mainMenuKeyboard.append([register])

    elif (not GetIsVerified(idTelegram=update.effective_chat.id)): # Il tuo account non è attivato
        risposta = """Ancora non ti è stato attivato l'account!
        Riceverai un messaggio appena la tua card sarà pronta!"""

        info = InlineKeyboardButton(text="❓ INFO ❓", callback_data="INFO")
        stop = InlineKeyboardButton(text="🛑 STOP 🛑", callback_data="STOP")

        mainMenuKeyboard.append([info])
        mainMenuKeyboard.append([stop])

    elif(not GetIsAdmin(idTelegram=update.effective_chat.id)): # Non sei amministratore
        username = GetUsername(idTelegram=update.effective_chat.id)        
        risposta = f"""Bentornato {username}, che vuoi fare?"""

        saldo = InlineKeyboardButton(text="📈 SALDO 📉", callback_data="SAL")
        info = InlineKeyboardButton(text="❓ INFO ❓", callback_data="INFO")
        stop = InlineKeyboardButton(text="🛑 STOP 🛑", callback_data="STOP")

        mainMenuKeyboard.append([saldo])
        mainMenuKeyboard.append([info])
        mainMenuKeyboard.append([stop])

    else: # Sei amministratores
        username = GetUsername(idTelegram=update.effective_chat.id)
        risposta = f"""Bentornato {username}, che vuoi fare?"""

        saldo = InlineKeyboardButton(text="📈 SALDO 📉", callback_data="SAL")
        addAdmin = InlineKeyboardButton(text="👨🏽‍🔧 AGGIUNGI ADMIN 👩🏽‍🔧", callback_data="ADD")
        remAdmin = InlineKeyboardButton(text="🚷 RIMUOVI ADMIN 🚷", callback_data="REM")
        info = InlineKeyboardButton(text="❓ INFO ❓", callback_data="INFO")
        stop = InlineKeyboardButton(text="🛑 STOP 🛑", callback_data="STOP")

        mainMenuKeyboard.append([saldo])
        mainMenuKeyboard.append([addAdmin])
        mainMenuKeyboard.append([remAdmin])
        mainMenuKeyboard.append([info])
        mainMenuKeyboard.append([stop])

    await update.message.reply_photo(photo=image, caption=risposta, reply_markup=InlineKeyboardMarkup(mainMenuKeyboard))

    return ConversationHandler.END