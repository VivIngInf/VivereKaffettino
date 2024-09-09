from Modules.Bot.New_Menu.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Modules.Bot.New_Menu.Utility import *
from Modules.Shared.Query import GetAulette, InsertUser, GetIdGruppoTelegram, GetAuletta
from Modules.Bot.New_Menu.Stop import stop_after_registration


class Registration(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = ["acquire_username", "acquire_age", "select_gender", "confirm_gender",
        #                         "select_auletta", "registration_done"]

        self.user_params = {
            "telegramID": 0,

            'acquire_username': "",

            "acquire_age": "",

            "select_gender": "",

            "confirm_gender": "",

            "select_auletta": "",
        }

        self.INTRO_MESSAGES = {

            "acquire_username": f"Digita l'username rispettando lo stardard Unipa con iniziali grandi.\n"
                                f"Es: Massimo.Midiri03",

            "acquire_age": "Digita la tua data di nascita rispettando il formato dell'esempio per favore.\n"
                           "Es: 11/09/2001",

            "select_gender": "Adesso seleziona il tuo genere per favore",

            "confirm_gender": ["Hai selezionato", ", confermi?"],

            "select_auletta": "Seleziona la tua Auletta di appartenenza",

        }

        # Get Aulette from DB
        buttons = []
        for auletta in GetAulette():
            auletta = str(auletta).split()
            button = InlineKeyboardButton(text=auletta[1], callback_data=auletta[1])
            buttons.append([button])
        buttons.append([InlineKeyboardButton("🔙 Torna indietro", callback_data='select_gender')])

        self.KEYBOARDS = {

            "acquire_username": InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]),

            "acquire_age": InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Torna indietro", callback_data='register')]]),

            "select_gender": InlineKeyboardMarkup(
                [[InlineKeyboardButton("Donna", callback_data='donna')],
                 [InlineKeyboardButton("Uomo", callback_data='uomo')],
                 [InlineKeyboardButton("Altro", callback_data='altro')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='acquire_age')]]),

            "confirm_gender": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔️ Conferma", callback_data='select_auletta')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='select_gender')]]),

            "select_auletta": InlineKeyboardMarkup(buttons),

        }

        self.ERROR_MESSAGES = {

            "acquire_username": "Hai digitato un username che non rispetta lo stardard Unipa, "
                                "riprova.\nEs: Massimo.Midiri03",

            "acquire_age": "Hai digitato una data di nascita che non rispetta lo stardard, "
                           "riprova.\nEs: 11/09/2001",
        }

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None, current_batch: str = None):
        self.query = query
        self.current_batch = current_batch
        await query.edit_message_text(self.INTRO_MESSAGES[current_batch], reply_markup=self.KEYBOARDS[current_batch])

    async def forward_conversation(self, query, context: ContextTypes.DEFAULT_TYPE, current_batch: str):
        self.query = query
        self.current_batch = current_batch
        self.user_params[current_batch] = query.data

        if current_batch == "confirm_gender":
            await query.edit_message_text(
                f"{self.INTRO_MESSAGES[current_batch][0]} {query.data.upper()} {self.INTRO_MESSAGES[current_batch][1]}",
                reply_markup=self.KEYBOARDS[current_batch])
        else:
            await query.edit_message_text(self.INTRO_MESSAGES[current_batch],
                                          reply_markup=self.KEYBOARDS[current_batch])

    async def acquire_conversation_param(self, context: ContextTypes.DEFAULT_TYPE, previous_batch: str,
                                         current_batch: str, next_batch: str, chat_id: int, message_id: int,
                                         typed_string: str, flag: bool):
        if flag:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✔ Conferma", callback_data=next_batch)],
                                             [InlineKeyboardButton("🔙 Torna indietro", callback_data=previous_batch)]])
            query = self.query
            self.user_params[current_batch] = typed_string
            self.current_batch = current_batch
            self.user_params["telegramID"] = chat_id
            await query.edit_message_text(text=f"Hai scritto {typed_string}, confermi?", reply_markup=keyboard)
        else:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            query = self.query
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Torna indietro", callback_data=previous_batch)]])
            await query.edit_message_text(self.ERROR_MESSAGES[current_batch], reply_markup=keyboard)

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
        # Since we are at the end, the last batch is "select_auletta"
        self.user_params["select_auletta"] = query.data
        await self.insert_user(context)
        buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text=f"{self.user_params['acquire_username']} "
                                           f"benvenut{GENDER_DICT[self.user_params['confirm_gender']]} in Vivere Kaffettino!",
                                      reply_markup=keyboard)
        context.user_data.pop("Registration")
        self.current_batch = ""
        await stop_after_registration(update, context)

    async def insert_user(self, context: ContextTypes.DEFAULT_TYPE):
        """Memorizza nel DB e avvisa gli admin"""
        InsertUser(idTelegram=str(self.user_params["telegramID"]), auletta=self.user_params["select_auletta"],
                   genere=self.convert_to_gender_db(self.user_params["confirm_gender"]),
                   dataNascita=self.user_params["acquire_age"],
                   username=self.user_params["acquire_username"])
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✔ Verifica",
                                   callback_data=f'instant_verify:{self.user_params["acquire_username"]}')],
             [InlineKeyboardButton("✖ Elimina",
                                   callback_data=f'instant_delete:{self.user_params["acquire_username"]}')]])

        await context.bot.send_message(chat_id=GetIdGruppoTelegram(GetAuletta(self.user_params["select_auletta"])),
                                       text=f'Ciao ragazzi, {self.user_params["acquire_username"]} si è appena registrato',
                                       reply_markup=keyboard)

    def get_current_batch(self) -> str:
        return self.current_batch

    @staticmethod
    def convert_to_gender_db(gender: str) -> str:
        """Ritorna solo la prima lettera del genere passato come parametro"""
        return gender[0].upper()

