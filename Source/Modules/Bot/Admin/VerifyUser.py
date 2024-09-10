from Modules.Bot.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Modules.Bot.Utility import *
from Modules.Shared.Query import (GetUnverifiedUsers, GetMyAuletta, assignCard, GetIdTelegram, getGender,
                                  SetIsVerified, removeUser)


class VerifyUser(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = ["verify_user", "acquire_username", "action_to_apply",
        # "acquire_card_number", "assign_card", "delete_user"]

        self.UNVERIFIED_USERS_LIST_KEYBOARD = None

        self.user_params = {
            "telegramID": 0,

            'acquire_username': "",

            "acquire_card_number": "",

        }

        self.KEYBOARDS = {

            "acquire_username": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Conferma", callback_data='action_to_apply')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='verify_user')]]),

            "action_to_apply": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Verifica", callback_data='acquire_card_number')],
                 [InlineKeyboardButton("✖ Elimina", callback_data='delete_user')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='verify_user')]]),

            "acquire_card_number": InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Torna indietro", callback_data='action_to_apply')]]),

            "assign_card": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Conferma", callback_data='assign_card')],
                [InlineKeyboardButton("🔙 Torna indietro", callback_data='action_to_apply')]]),

        }

        self.INTRO_MESSAGES = {

            "verify_user": "Scegli chi abilitare tramite i bottoni oppure scrivi il nome utente in chat",

            "acquire_username": "Hai scelto",

            "action_to_apply": "Cosa vuoi fare?",

            "acquire_card_number": "Digita l'ID CARD da assegnare all'utente",


        }

        self.WARNING_MESSAGES = {

            "acquire_username": "Non sei abilitato ad attivare questo utente "
                                "in quanto non appartiente alla tua Auletta.\n"
                                "Riprova o seleziona l'utente con i bottoni.",

            "acquire_card_number": "ID CARD non valido, inserire un valore "
                                   "strettamente numerico!",

        }

        self.ERROR_MESSAGES = {

            "verify_user": "Non ci sono utenti da verificare",

            "acquire_username": "Utente non trovato, riprova o seleziona l'utente con i bottoni",

            "acquire_card_number": "L'ID CARD esiste già, riprova"

        }

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch

        admin_who_makes_the_query = query.from_user.id

        buttons = []
        for utente in GetUnverifiedUsers(GetMyAuletta(admin_who_makes_the_query)):
            button = InlineKeyboardButton(text=utente[0], callback_data=utente[0])
            buttons.append([button])
        buttons.append([InlineKeyboardButton("🔙 Torna indietro", callback_data='main_admin')])
        self.UNVERIFIED_USERS_LIST_KEYBOARD = InlineKeyboardMarkup(buttons)

        if len(buttons) == 1:
            await query.edit_message_text(self.ERROR_MESSAGES[current_batch],
                                          reply_markup=self.UNVERIFIED_USERS_LIST_KEYBOARD)
        else:
            await query.edit_message_text(self.INTRO_MESSAGES[current_batch],
                                          reply_markup=self.UNVERIFIED_USERS_LIST_KEYBOARD)

    async def forward_conversation(self, query, context: ContextTypes.DEFAULT_TYPE, current_batch: str):
        self.query = query
        self.current_batch = current_batch
        self.user_params[current_batch] = query.data
        await query.edit_message_text(self.INTRO_MESSAGES[current_batch], reply_markup=self.KEYBOARDS[current_batch])

    async def acquire_conversation_param(self, context: ContextTypes.DEFAULT_TYPE, previous_batch: str,
                                         current_batch: str, next_batch: str, chat_id: int, message_id: int,
                                         typed_string: str, flag: bool, flag2: bool = None):

        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        if flag:
            if flag2:
                query = self.query
                await query.edit_message_text(text=self.WARNING_MESSAGES[current_batch],
                                              reply_markup=self.keyboard_to_show(current_batch, flag2))
            else:
                query = self.query
                self.user_params[current_batch] = typed_string
                self.current_batch = current_batch
                self.user_params["telegramID"] = chat_id
                await query.edit_message_text(self.text_to_send(current_batch=current_batch,
                                                                optional_param=typed_string),
                                              reply_markup=self.keyboard_to_show(current_batch, flag2, next_batch))
        else:
            query = self.query
            await query.edit_message_text(text=self.ERROR_MESSAGES[current_batch],
                                          reply_markup=self.keyboard_to_show(current_batch, flag2, next_batch, flag))

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
        assignCard(GetIdTelegram(self.user_params["acquire_username"]), self.user_params["acquire_card_number"])
        idTelegram = GetIdTelegram(username=self.user_params["acquire_username"])
        gender = getGender(idTelegram=idTelegram)
        SetIsVerified(GetIdTelegram(self.user_params["acquire_username"]))

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Ritorna al menu admin", callback_data='main_admin')]])
        await self.query.edit_message_text(
            text=f"L'utente {self.user_params['acquire_username']} è stato verificato correttamente!",
            reply_markup=keyboard)

        # Alerting the user that it has been verified
        await context.bot.send_message(chat_id=GetIdTelegram(self.user_params["acquire_username"]),
                                       text=f'{self.user_params["acquire_username"]}, '
                                            f'sei stat{DB_GENDER_DICT[gender]} abilitat{DB_GENDER_DICT[gender]} '
                                            f'ad usare Vivere Kaffettino.\n\nVieni in auletta per ritirare la card!'
                                            f'\n\nPremi /start per iniziare e goditi i tuoi caffè! :)')
        self.current_batch = ""

    async def bad_ending_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
        removeUser(GetIdTelegram(self.user_params["acquire_username"]))
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Torna indietro", callback_data='verify_user')]])
        await query.edit_message_text(
            text=f"L'utente {self.user_params['acquire_username']} è stato rimosso correttamente!",
            reply_markup=keyboard)
        self.current_batch = ""

    def text_to_send(self, optional_param: str = None, current_batch: str = None) -> str:
        if current_batch == "acquire_username":
            return f"{self.INTRO_MESSAGES[current_batch]} {optional_param}, confermi?"
        elif current_batch == "acquire_card_number":
            return (f"Sicuro di voler confermare {self.user_params['acquire_username']} "
                    f"con idCard: {self.user_params['acquire_card_number']}?")

    def keyboard_to_show(self, current_batch: str = None, flag2: bool = False, next_batch: str = None,
                         flag: bool = True) -> str:
        """Base on the current batch the keyboard to show need is different"""
        if current_batch == "acquire_username" and flag2:
            return self.UNVERIFIED_USERS_LIST_KEYBOARD
        elif current_batch == "acquire_card_number" and flag:
            return self.KEYBOARDS[next_batch]
        elif current_batch == "acquire_card_number" and not flag:
            return self.KEYBOARDS[current_batch]
        else:
            return self.KEYBOARDS[self.current_batch]
