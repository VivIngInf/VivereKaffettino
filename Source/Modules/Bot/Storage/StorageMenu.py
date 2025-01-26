from Modules.Bot.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


class StorageMenu(SubMenu):

    def __init__(self):
        super().__init__()

        self.INTRO_MESSAGES = {

            "main_storage": "GESTIONE MAGAZZINO"
        }

        self.KEYBOARDS = {

            "main_storage": InlineKeyboardMarkup(
                [[InlineKeyboardButton("Rimuovi Prodotto 🟥", callback_data='remove_product_storage')],
                 [InlineKeyboardButton("Aggiungi Prodotto ➕", callback_data='select_new_product')],
                 [InlineKeyboardButton("🔙 Ritorna al menu admin", callback_data='back_main_menu')]])
        }

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch
        await query.edit_message_text(self.INTRO_MESSAGES[current_batch], reply_markup=self.KEYBOARDS[current_batch])

