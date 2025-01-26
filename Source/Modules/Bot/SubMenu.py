from telegram.ext import ContextTypes
from telegram import Update


class SubMenu:

    def __init__(self):
        self.query = None
        self.current_batch = ""

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """The first part of the conversation"""

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """The last part of the conversation"""

    async def forward_conversation(self, query, context: ContextTypes.DEFAULT_TYPE, current_batch: str):
        """Concatenate the current batch to the next one"""

    async def acquire_conversation_param(self, context: ContextTypes.DEFAULT_TYPE, previous_batch: str,
                                         current_batch: str, next_batch: str, chat_id: int, message_id: int,
                                         typed_string: str, flag: bool):
        """Just get actual typed string"""

    def get_current_batch(self) -> str:
        """
        Imagine the Bot says: "Write your username". Then our current batch is acquire_username.
        So this variable represents the current state of the conversation. You can find:

        - self.current_batch = current_batch
        - self.current_batch = next_batch

        But the meaning is that we are referring to the current topic of the conversation, given by the
        message sent by the bot.
        """
        return self.current_batch

    def text_to_send(self, optional_param: str = None) -> str:
        """Base on the current batch the message to send need to be manipulated"""
