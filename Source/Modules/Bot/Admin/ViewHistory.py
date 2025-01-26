from Modules.Bot.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Modules.Bot.Utility import *
from telegram.constants import ParseMode
from Modules.Shared.Query import GetIdTelegram, GetVerifiedUsers, GetMyAuletta
from Modules.Bot.History import get_history


class ViewHistory(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = ["user_history", "acquire_username"]

        self.KEYBOARDS = {

            "user_history": InlineKeyboardMarkup(
                 [[InlineKeyboardButton("🔙 Torna indietro", callback_data='main_admin')]]),

            "acquire_username": InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Torna indietro", callback_data='user_history')]]),
        }

        self.INTRO_MESSAGES = {

            "user_history": "Scegli a chi visionare lo storico tramite i bottoni oppure scrivi il nome utente in chat",

            "acquire_username": "Hai scelto",

        }

        self.WARNING_MESSAGES = {

            "acquire_username": "Non sei abilitato a visionare questo utente "
                                "in quanto non appartiente alla tua Auletta, riprova!"


        }

        self.ERROR_MESSAGES = {

            "user_history": "Non ci sono utenti in questa Auletta 😢",

            "acquire_username": "Utente non trovato, riprova!",

        }

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch

        admin_who_makes_the_query = query.from_user.id

        buttons = []
        for utente in GetVerifiedUsers(GetMyAuletta(admin_who_makes_the_query)):
            if str(utente[0]).split(".")[0] != "Auletta":
                button = InlineKeyboardButton(text=utente[0], callback_data=utente[0] + "h")
                buttons.append([button])
        buttons.append([InlineKeyboardButton("🔙 Torna indietro", callback_data='main_admin')])
        self.VERIFIED_USERS_LIST_KEYBOARD = InlineKeyboardMarkup(buttons)

        if len(buttons) == 1:
            await query.edit_message_text(self.ERROR_MESSAGES[current_batch],
                                          reply_markup=self.VERIFIED_USERS_LIST_KEYBOARD)
        else:
            await query.edit_message_text(self.INTRO_MESSAGES[current_batch],
                                          reply_markup=self.VERIFIED_USERS_LIST_KEYBOARD)

    async def acquire_conversation_param(self, context: ContextTypes.DEFAULT_TYPE, previous_batch: str,
                                         current_batch: str, next_batch: str, chat_id: int, message_id: int,
                                         typed_string: str, flag: bool, flag2: bool = None):

        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        if flag:
            if flag2:
                query = self.query
                await query.edit_message_text(text=self.WARNING_MESSAGES[current_batch],
                                              reply_markup=self.KEYBOARDS[current_batch])
            else:
                query = self.query
                self.current_batch = ""
                await query.edit_message_text(text=get_history(GetIdTelegram(typed_string)),
                                              reply_markup=self.KEYBOARDS[current_batch],
                                              parse_mode=ParseMode.MARKDOWN)
        else:
            query = self.query
            await query.edit_message_text(text=self.ERROR_MESSAGES[current_batch],
                                          reply_markup=self.VERIFIED_USERS_LIST_KEYBOARD)

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
        self.current_batch = ""
