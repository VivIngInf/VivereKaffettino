from Modules.Bot.New_Menu.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Modules.Shared.Query import getIDCard, GetIdTelegram, assignCard


class ChangeCard(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = ["change_card", "acquire_username", "acquire_card",
        # "acquire_card_number", "change_card_done"]

        self.user_params = {
            "telegramID": 0,

            "acquire_username": "",

            "acquire_card": "",

            "acquire_card_number": ""

        }

        self.INTRO_MESSAGES = {

            "change_card": "Digita l'username dell'utente di cui cambiare l'ID CARD",

            "acquire_username": "Sicuro di voler confermare",

            "acquire_card": "è il vecchio ID CARD, digita quello nuovo",

            "acquire_card_number": "Sicuro di voler confermare"
        }

        self.KEYBOARDS = {

            "change_card": InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Annulla", callback_data='main_admin')]]),

            "acquire_username": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Conferma", callback_data='acquire_card_to_change')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='main_admin')]]),

            "acquire_card_number": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Conferma", callback_data='change_card_done')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='change_card')]])
        }

        self.WARNING_KEYBOARDS = {

            "acquire_username": InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Torna indietro", callback_data='main_admin')]]),

            "acquire_card": InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Torna Indietro", callback_data='change_card')]]),

            "acquire_card_number": InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Torna Indietro", callback_data='change_card')]]),

        }

        self.WARNING_MESSAGES = {

            "acquire_username": "Utente non trovato, riprova o torna al menu admin",

            "acquire_card": "Non è assegnato alcun ID CARD al momento.\nDigita il nuovo ID CARD",

            "acquire_card_number": "ID CARD non valido, inserire un valore "
                                   "strettamente numerico!",
        }

        self.ERROR_MESSAGES = {}

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch
        await query.edit_message_text(self.INTRO_MESSAGES[current_batch], reply_markup=self.KEYBOARDS[current_batch])

    async def forward_conversation(self, query, context: ContextTypes.DEFAULT_TYPE, current_batch: str):
        self.query = query
        self.current_batch = current_batch
        self.user_params[current_batch] = query.data
        id_card_exist = getIDCard(GetIdTelegram(self.user_params['acquire_username'])) == 0
        await query.edit_message_text(self.text_to_send(None, current_batch, id_card_exist),
                                      reply_markup=self.WARNING_KEYBOARDS[current_batch])

    async def acquire_conversation_param(self, context: ContextTypes.DEFAULT_TYPE, previous_batch: str,
                                         current_batch: str, next_batch: str, chat_id: int, message_id: int,
                                         typed_string: str, flag: bool, flag2: bool = None):
        # current = acquire_card_number

        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        if flag:
            if flag2:
                query = self.query
                await query.edit_message_text(text=self.WARNING_MESSAGES[current_batch],
                                              reply_markup=self.WARNING_KEYBOARDS[current_batch])
            else:
                query = self.query
                self.user_params[current_batch] = typed_string
                self.current_batch = current_batch
                self.user_params["telegramID"] = chat_id
                await query.edit_message_text(self.text_to_send(current_batch=current_batch,
                                                                optional_param=typed_string),
                                              reply_markup=self.KEYBOARDS[current_batch])

        else:
            query = self.query
            await query.edit_message_text(text=self.ERROR_MESSAGES[current_batch],
                                          reply_markup=self.KEYBOARDS[current_batch])

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
        assignCard(GetIdTelegram(self.user_params["acquire_username"]),
                   self.user_params["acquire_card_number"])
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Torna al menu admin", callback_data='main_admin')]])
        await query.edit_message_text(
            f"Adesso l'ID CARD di {self.user_params['acquire_username']} è {self.user_params['acquire_card_number']}",
            reply_markup=keyboard)
        self.current_batch = ""

    def text_to_send(self, optional_param: str = None, current_batch: str = None, flag: bool = None) -> str:
        """Base on the current batch the message to send need to be manipulated"""
        if current_batch == "acquire_username":
            return f"{self.INTRO_MESSAGES[current_batch]} {optional_param}?"
        elif current_batch == "acquire_card" and flag:
            return self.WARNING_MESSAGES[current_batch]
        elif current_batch == "acquire_card" and not flag:
            return (f"{getIDCard(GetIdTelegram(self.user_params['acquire_username']))} "
                    f"{self.INTRO_MESSAGES[current_batch]}")
        else:
            return f"{self.INTRO_MESSAGES[current_batch]} {optional_param}?"
