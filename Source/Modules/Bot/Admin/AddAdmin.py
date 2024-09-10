from Modules.Bot.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Modules.Shared.Query import SetAdminDB, GetIdTelegram


class AddAdmin(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = ["add_admin", "acquire_username", "done"]

        self.INTRO_MESSAGES = {

            "add_admin": "Digita l'username dell'utente da far diventare admin",

            "acquire_username": ["Ok, l'utente", "è stato promosso ad Admin"]

        }

        self.KEYBOARDS = {

            "add_admin": InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", callback_data='main_admin')]]),

            "acquire_username": InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Annulla", callback_data='main_admin')]]),

            "done": InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Ritorna al menu admin", callback_data='main_admin')]])

        }

        self.WARNING_MESSAGES = {

            "acquire_username": "L'utente è già un Admin!"

        }

        self.ERROR_MESSAGES = {

            "acquire_username": "Utente non trovato riprova oppure annulla",

        }

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch
        await query.edit_message_text(self.INTRO_MESSAGES[current_batch], reply_markup=self.KEYBOARDS[current_batch])

    async def acquire_conversation_param(self, context: ContextTypes.DEFAULT_TYPE, previous_batch: str,
                                         current_batch: str, next_batch: str, chat_id: int, message_id: int,
                                         typed_string: str, flag: bool, flag2: bool = None, typed_num: float = None):

        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        if flag:
            if flag2:
                query = self.query
                await query.edit_message_text(text=self.WARNING_MESSAGES[current_batch],
                                              reply_markup=self.KEYBOARDS[next_batch])
            else:
                query = self.query
                self.current_batch = next_batch
                SetAdminDB(GetIdTelegram(username=typed_string), True)
                await query.edit_message_text(f"{self.INTRO_MESSAGES[current_batch][0]} "
                                              f"{typed_string} {self.INTRO_MESSAGES[current_batch][1]}",
                                              reply_markup=self.KEYBOARDS[next_batch])

        else:
            query = self.query
            await query.edit_message_text(text=self.ERROR_MESSAGES[current_batch],
                                          reply_markup=self.KEYBOARDS[current_batch])
