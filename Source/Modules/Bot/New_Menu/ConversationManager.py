from telegram.ext import ContextTypes


class ConversationManager:

    def __init__(self):
        self.active_conversation = ""
        self.current_batch = ""

    def set_active_conversation(self, active_conversation: str):
        """
        Get the name of current conversation, which is one of these:
        - Registration

        """
        self.active_conversation = active_conversation
        if active_conversation == '':
            self.current_batch = ""

    def get_active_conversation(self) -> str:
        """
        Get the name of current conversation, which is one of these:
        - Registration

        """

        return self.active_conversation if self.active_conversation else "None"

    def get_current_conversation_batch(self, context: ContextTypes.DEFAULT_TYPE) -> str:
        conversation = context.user_data.get(self.active_conversation)
        return conversation.get_current_batch() if conversation else "None"
