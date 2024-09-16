from Modules.Bot.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


class AdminMenu(SubMenu):

    def __init__(self):
        super().__init__()

        self.INTRO_MESSAGES = {

            "main_admin": "GESTIONE ADMIN",
        }

        self.KEYBOARDS = {

            "main_admin": InlineKeyboardMarkup(
                [[InlineKeyboardButton("Verifica Utente ☑", callback_data='verify_user')],
                 [InlineKeyboardButton("Cambia Tessera 🔄", callback_data='change_card')],
                 [InlineKeyboardButton("Gestione Tessera ⏯", callback_data='manage_card')],
                 [InlineKeyboardButton("Aggiungi Admin 🟢", callback_data='add_admin')],
                 [InlineKeyboardButton("Rimuovi Admin 🔴", callback_data='remove_admin')],
                 [InlineKeyboardButton("Resoconto Utenti Excel 📃", callback_data='send_resoconto')],
                 [InlineKeyboardButton("Manda messaggio a tutti gli utenti 📣",
                                       callback_data='send_message_to_everyone')],
                 [InlineKeyboardButton("Crea utente illimitato ♾", callback_data='unlimited_user')],
                 [InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]),

        }

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch
        await query.edit_message_text(self.INTRO_MESSAGES[current_batch], reply_markup=self.KEYBOARDS[current_batch])



