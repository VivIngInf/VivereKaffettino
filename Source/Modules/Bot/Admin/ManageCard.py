from Modules.Bot.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


class ManageCard(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = []

        self.user_params = {
            "telegramID": 0,
        }

        self.INTRO_MESSAGES = {
            "manage_card": "GESTIONE TESSERA"
        }

        self.KEYBOARDS = {

            "manage_card": InlineKeyboardMarkup(
                [[InlineKeyboardButton("Abilita Card ✅", callback_data='activate_card')],
                 [InlineKeyboardButton("Disabilita Card ⛔", callback_data='deactivate_card')],
                 [InlineKeyboardButton("🔙 Ritorna al menu tessera", callback_data='main_admin')]])
        }

        self.WARNING_MESSAGES = {
        }

        self.ERROR_MESSAGES = {
        }

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch
        await query.edit_message_text(self.INTRO_MESSAGES[current_batch], reply_markup=self.KEYBOARDS[current_batch])
