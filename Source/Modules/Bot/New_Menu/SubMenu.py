from telegram.ext import ContextTypes
from telegram import Update


class SubMenu:

    def __init__(self):
        self.query = None
        self.current_batch = ""

    async def start_conversation(self, update: Update, current_batch: str, query=None):
        """The first part of the conversation"""

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query):
        """The last part of the conversation"""

    async def forward_conversation(self, query, context: ContextTypes.DEFAULT_TYPE, current_batch: str):
        """Concatenate the current batch to the next one"""

    async def acquire_conversation_param(self, context: ContextTypes.DEFAULT_TYPE, previous_batch: str,
                                         current_batch: str, next_batch: str, chat_id: int, message_id: int,
                                         typed_string: str, flag: bool):
        """Just get actual typed string"""

    def get_current_batch(self) -> str:
        return self.current_batch

    async def bot_send_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Use this function to send a message with the bot"""
