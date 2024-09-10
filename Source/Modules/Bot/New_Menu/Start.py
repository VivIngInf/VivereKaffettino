import os
import random
from datetime import datetime
from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from ...Shared.Query import GetIsAdmin, CheckUserExists, GetIsVerified, GetUsername
from Modules.Bot.New_Menu.Utility import *
from Modules.Bot.New_Menu.SubMenu import SubMenu
from Modules.Bot.New_Menu.Registration import Registration
from Modules.Bot.New_Menu.Recharge import Recharge
from Modules.Bot.New_Menu.AdminMenu import AdminMenu
from Modules.Bot.New_Menu.VerifyUser import VerifyUser
from Modules.Bot.New_Menu.ConversationManager import ConversationManager


class Start(SubMenu):

    def __init__(self):
        super().__init__()

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        image: InputFile = self.SendRandomImage()
        caption = "☕ Benvenuto su vivere kaffettino! ☕"

        text = ""
        mainMenuKeyboard = []
        classes_to_generate = {"ConversationManager": ConversationManager()}

        # ----- BOTTONI -----

        register = InlineKeyboardButton(text="📝 REGISTRATI 📝", callback_data="register")
        saldo = InlineKeyboardButton(text="📈 SALDO 📉", callback_data="balance")
        ricarica = InlineKeyboardButton(text="💸 RICARICA 💸", callback_data="recharge")
        admin = InlineKeyboardButton(text="👨🏽‍🔧 ADMIN MENU 🏽‍🔧", callback_data="main_admin")
        storage = InlineKeyboardButton(text="👨🏽‍🔧 GESTIONE MAGAZZINO 🗄🔧", callback_data="storage")
        info = InlineKeyboardButton(text="❓ INFO ❓", callback_data="info")
        removeUser = InlineKeyboardButton(text="❌ ELIMINA RICHIESTA ❌",
                                          callback_data="delete_request_registration_account")
        stop = InlineKeyboardButton(text="🛑 STOP 🛑", callback_data="stop")

        # -------------------

        if (not CheckUserExists(idTelegram=update.effective_chat.id)):  # Non sei ancora registrato
            text = "👀 Hey, è la prima volta che visiti vivere kaffetino? 👀\n🔻 Registrati premendo il bottone sottostante! 🔻"

            classes_to_generate |= {"Registration": Registration()}
            mainMenuKeyboard.append([register])
            mainMenuKeyboard.append([stop])

        elif (not GetIsVerified(idTelegram=update.effective_chat.id)):  # Il tuo account non è attivato
            text = "🛑 Ancora non ti è stato attivato l'account! 🛑\nRicordati di andare in auletta e pagare 1€ per avevere la tua card!"

            mainMenuKeyboard.append([info])
            mainMenuKeyboard.append([removeUser])
            mainMenuKeyboard.append([stop])

        elif (not GetIsAdmin(idTelegram=update.effective_chat.id)):  # Non sei amministratore
            username = GetUsername(idTelegram=update.effective_chat.id)
            text = f"👋🏽 {username}, è un piacere rivederti! 👋🏽\nChe vuoi fare? 👀"

            mainMenuKeyboard.append([saldo])
            mainMenuKeyboard.append([info])
            mainMenuKeyboard.append([stop])

        else:  # Sei amministratore
            username = GetUsername(idTelegram=update.effective_chat.id)
            text = f"👋🏽 {username}, è un piacere rivederti! 👋🏽\nChe vuoi fare? 👀"

            classes_to_generate |= {"Recharge": Recharge(), "Admin": AdminMenu(), "VerifyUser": VerifyUser()}

            mainMenuKeyboard.append([saldo])
            mainMenuKeyboard.append([ricarica])
            mainMenuKeyboard.append([admin])
            mainMenuKeyboard.append([storage])
            mainMenuKeyboard.append([info])
            mainMenuKeyboard.append([stop])

        keyboard = InlineKeyboardMarkup(mainMenuKeyboard)

        # Verifico se è il primo avvio o meno
        if "first_start" not in context.user_data:
            await update.message.reply_photo(
                photo=image,
                caption=caption
            )
            initial_message = await update.message.reply_text(text=text, reply_markup=keyboard)
            context.user_data['first_start'] = True
            context.user_data['initial_message'] = initial_message
            for key, value in classes_to_generate.items():
                context.user_data[key] = value
        else:
            await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    @staticmethod
    def GiornoCorrente() -> str:
        """Get current day of the week"""
        weekdays: list = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        return weekdays[datetime.now().weekday()]

    def GiornoFestivo(self):
        """Verify if current date is a festivity day"""

        current_date = datetime.now()
        pasqua: datetime = self.calcola_pasqua(datetime.now().year)

        festive_dates = [
            (12, 13),  # Santa Lucia (13 dicembre)
            (12, 24),  # Vigilia Natale (24 dicembre)
            (12, 25),  # Natale (25 dicembre)
            (pasqua.month, pasqua.day),  # Pasqua
            (pasqua.month, pasqua.day + 1)  # Pasquetta
            # Aggiungi altre festività qui
        ]

        return (current_date.month, current_date.day) in festive_dates

    @staticmethod
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

    def SendRandomImage(self) -> InputFile:
        """'Sta funzione l'ha fatta chatGPT, non mi volevo studiare come funzionasse l'algoritmo kekw"""

        # Determina la data attuale
        current_date = datetime.now()

        # Elenco delle possibili cartelle in cui cercare le immagini
        possible_folders = []

        # Verifica se è dicembre
        if current_date.month == 12:
            possible_folders.append('Natale')

        # Verifica se è Pasqua o Pasquetta
        pasqua_date = self.calcola_pasqua(current_date.year)

        if (current_date.month, current_date.day) == (pasqua_date.month, pasqua_date.day):
            possible_folders.append('Pasqua')
        elif (current_date.month, current_date.day) == (pasqua_date.month, pasqua_date.day + 1):
            possible_folders.append('Pasquetta')

        # Verifica se è Santa Lucia
        if (current_date.month, current_date.day) == (12, 13):
            possible_folders.append('Santa Lucia')

        # Se non è un giorno festivo, aggiungi 'generiche' e la cartella specifica del giorno della settimana
        if not possible_folders:
            possible_folders.extend(['Generiche', self.GiornoCorrente()])

        # Seleziona casualmente una cartella tra quelle possibili
        selected_folder = random.choice(possible_folders)

        # Ottieni il percorso completo della cartella selezionata
        modulePath = os.path.dirname(os.path.abspath(__file__))  # Otteniamo il percorso di questo file

        while os.path.basename(modulePath) != 'VivereKaffettino':
            modulePath = os.path.dirname(modulePath)

        folder_path = os.path.join(modulePath, "Resources", "Images", selected_folder)

        # Ottieni la lista dei file nella cartella selezionata
        image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

        if image_files:
            # Seleziona casualmente un'immagine dalla cartella selezionata
            random_image = random.choice(image_files)

            # Costruisci il percorso completo del file selezionato
            image_path = os.path.join(folder_path, random_image)

            # Invia l'immagine all'utente
            return open(image_path, 'rb')
