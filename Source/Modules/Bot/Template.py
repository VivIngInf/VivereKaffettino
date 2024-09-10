from Modules.Bot.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


class Template(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = []

        self.user_params = {
            "telegramID": 0,
        }

        self.INTRO_MESSAGES = {
        }

        self.KEYBOARDS = {
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

    async def forward_conversation(self, query, context: ContextTypes.DEFAULT_TYPE, current_batch: str):
        self.query = query
        self.current_batch = current_batch
        self.user_params[current_batch] = query.data
        await query.edit_message_text(self.text_to_send(), reply_markup=self.KEYBOARDS[current_batch])

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
                self.user_params[current_batch] = typed_string
                self.current_batch = current_batch
                self.user_params["telegramID"] = chat_id
                await query.edit_message_text(self.text_to_send(current_batch=current_batch,
                                                                optional_param=typed_string),
                                              reply_markup=self.keyboard_to_show(current_batch))

        else:
            query = self.query
            await query.edit_message_text(text=self.ERROR_MESSAGES[current_batch],
                                          reply_markup=self.KEYBOARDS[current_batch])

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
        self.current_batch = ""

    def text_to_send(self, optional_param: str = None, current_batch: str = None) -> str:
        """Base on the current batch the message to send need to be manipulated"""
        return optional_param

    def keyboard_to_show(self, current_batch: str = None) -> str:
        """Base on the current batch the keyboard to show need is different"""
        return self.KEYBOARDS[current_batch]

