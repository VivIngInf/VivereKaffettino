from Modules.Bot.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from Modules.Shared.Query import GetNomeAuletta, GetMyAuletta, InsertInfiniteUser, GetIdGruppoTelegram, GetAuletta, \
    GetUsername


class UnlimitedUser(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = ["unlimited_user", "acquire_username", "acquire_card_unlimited",
        # "acquire_card", "confirm_data_unlimited"]

        self.user_params = {

            "admin_id": "",

            "auletta": "",

            "acquire_username": "",

            "acquire_card": ""
        }

        self.INTRO_MESSAGES = {

            "unlimited_user": "Dimmi il solo nome della tua Aula, al resto penso io.\n"
                              "Es 'Medicina' diventa 'Auletta.Medicina'",

            "acquire_username": "Sicuro?",

            "acquire_card_unlimited": "Digita il numero della carta",

            "acquire_card": "Sicuro?",

            "confirm_data_unlimited": "Sicuro di voler confermare i seguenti dati?\n"
                                      "L'operazione non può essere annullata e tutti saranno avvisati."
        }

        self.KEYBOARDS = {

            "acquire_username": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔️ Conferma", callback_data='acquire_card_unlimited')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='main_admin')]]),

            "acquire_card_unlimited": InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Torna indietro", callback_data='unlimited_user')]]),

            "acquire_card": InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Torna indietro", callback_data='unlimited_user')]]),

            "secure_confirm": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔️ Conferma", callback_data='confirm_data_unlimited')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='acquire_card_unlimited')]]),

            "confirm_data_unlimited": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔️ Conferma", callback_data='create_unlimited_user')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='acquire_card_unlimited')]])
        }

        self.WARNING_MESSAGES = {

            "acquire_card": "ID CARD non valido, inserire un valore "
                            "strettamente numerico!"

        }

        self.ERROR_MESSAGES = {

            "acquire_card": "L'ID CARD esiste già, riprova"
        }

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch
        admin_who_makes_the_query = query.from_user.id
        self.user_params["admin_id"] = admin_who_makes_the_query
        await query.edit_message_text(self.INTRO_MESSAGES[current_batch])

    async def forward_conversation(self, query, context: ContextTypes.DEFAULT_TYPE, current_batch: str):
        self.query = query
        self.current_batch = current_batch
        admin_who_makes_the_query = query.from_user.id
        auletta = GetNomeAuletta(GetMyAuletta(admin_who_makes_the_query))
        self.user_params["auletta"] = auletta
        await query.edit_message_text(self.text_to_send(current_batch=current_batch),
                                      reply_markup=self.KEYBOARDS[current_batch])

    async def acquire_conversation_param(self, context: ContextTypes.DEFAULT_TYPE, previous_batch: str,
                                         current_batch: str, next_batch: str, chat_id: int, message_id: int,
                                         typed_string: str, flag: bool, flag2: bool = None, typed_num: float = None):

        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        if flag:
            if flag2:
                query = self.query
                await query.edit_message_text(text=self.WARNING_MESSAGES[current_batch],
                                              reply_markup=self.keyboard_to_show(current_batch, flag2,
                                                                                 next_batch, flag))
            else:
                query = self.query
                self.user_params[current_batch] = f"Auletta.{typed_string}" if current_batch == "acquire_username" else typed_string
                self.current_batch = current_batch
                await query.edit_message_text(self.INTRO_MESSAGES[current_batch],
                                              reply_markup=self.keyboard_to_show(current_batch, flag2,
                                                                                 next_batch, flag))

        else:
            query = self.query
            await query.edit_message_text(text=self.ERROR_MESSAGES[current_batch],
                                          reply_markup=self.keyboard_to_show(current_batch, flag2,
                                                                             next_batch, flag))

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):

        username = self.user_params["acquire_username"]
        auletta = self.user_params["auletta"]
        ID_Card = self.user_params["acquire_card"]
        admin_username = GetUsername(self.user_params["admin_id"])
        InsertInfiniteUser(username, auletta, ID_Card)
        await context.bot.send_message(chat_id=GetIdGruppoTelegram(GetAuletta(self.user_params["auletta"])),
                                       text=f'Ciao ragazzi, {admin_username} ha creato un utente illimitato '
                                            f'avente i seguenti dati\n'
                                            f"Username -> {self.user_params['acquire_username']}\n"
                                            f"IDCARD   -> {self.user_params['acquire_card']}\n"
                                            f"Auletta  -> {self.user_params['auletta']}"
                                       )
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Ritorna al menu admin", callback_data='main_admin')]])
        await query.edit_message_text(text="Utente illimitato creato con successo!", reply_markup=keyboard)
        self.current_batch = ""

    def text_to_send(self, optional_param: str = None, current_batch: str = None) -> str:
        if current_batch == "confirm_data_unlimited":
            return (f"{self.INTRO_MESSAGES[current_batch]}\n"
                    f"Username -> {self.user_params['acquire_username']}\n"
                    f"IDCARD   -> {self.user_params['acquire_card']}\n"
                    f"Auletta  -> {self.user_params['auletta']}")
        else:
            return self.INTRO_MESSAGES[current_batch]

    def keyboard_to_show(self, current_batch: str = None, flag2: bool = False, next_batch: str = None,
                         flag: bool = True) -> str:
        """Base on the current batch the keyboard to show need is different"""
        if current_batch == "acquire_card" and not flag:
            return self.KEYBOARDS[current_batch]
        elif current_batch == "acquire_card" and flag2:
            return self.KEYBOARDS[current_batch]
        elif current_batch == "acquire_username":
            return self.KEYBOARDS[current_batch]
        else:
            return self.KEYBOARDS[next_batch]
