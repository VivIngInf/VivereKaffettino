from Modules.Bot.New_Menu.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Modules.Bot.New_Menu.Utility import *
from Modules.Shared.Query import incrementaSaldo, GetIdTelegram


class Recharge(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = ["acquire_username", "acquire_amount", "recharge_done"]

        self.user_params = {
            "telegramID": 0,

            'acquire_username': "",

            "acquire_amount": 0.,

            "recharge_done": False
        }

        self.INTRO_MESSAGES = {

            "acquire_username": "Digita l'username dell'utente che vuoi ricaricare",

            "acquire_amount": "Digita l'importo da ricaricare",

            "recharge_done": "Sicuro di voler confermare"

        }

        self.KEYBOARDS = {

            "acquire_username": InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]),

            "acquire_amount": InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]),

            "recharge_done": InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Conferma", callback_data='recharge_done')],
                 [InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]])

        }

        self.WARNING_MESSAGES = {

            "acquire_username": "Sorry ma non puoi ricaricare te stesso, "
                                "riprova oppure annulla e ritorna al menu principale",

            "acquire_amount": "La ricarica deve essere positiva!"
        }

        self.ERROR_MESSAGES = {

            "acquire_username": "Utente non trovato riprova oppure annulla e ritorna al menu principale",

            "acquire_amount": "Inserire un importo numerico valido!"
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
                                              reply_markup=self.KEYBOARDS[current_batch])
            else:
                query = self.query
                self.user_params[current_batch] = typed_string if typed_num is None else typed_num
                self.current_batch = next_batch
                self.user_params["telegramID"] = chat_id

                if current_batch != "acquire_amount":
                    await query.edit_message_text(text=self.INTRO_MESSAGES[next_batch],
                                                  reply_markup=self.KEYBOARDS[current_batch])
                else:
                    await query.edit_message_text(f"{self.INTRO_MESSAGES[next_batch]} {typed_num}?",
                                                  reply_markup=self.KEYBOARDS[next_batch])

        else:
            query = self.query
            await query.edit_message_text(text=self.ERROR_MESSAGES[current_batch],
                                          reply_markup=self.KEYBOARDS[current_batch])

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]])

        incrementaSaldo(usernameBeneficiario=self.user_params['acquire_username'],
                        IDTelegramAmministratore=query.from_user.id, ricarica=self.user_params["acquire_amount"])

        await query.edit_message_text(
            text=f"Ricarica a {self.user_params['acquire_username']} effettuata!\nTorna pure al menu principale",
            reply_markup=keyboard)

        await context.bot.send_message(chat_id=GetIdTelegram(self.user_params['acquire_username']),
                                       text=f'Ciao {self.user_params["acquire_username"]}, ricarica di '
                                            f'{self.user_params["acquire_amount"]} effettuata grazie e '
                                            f'goditi i tuoi caffè! :)')

        context.user_data.pop("Recharge")
        self.current_batch = ""

