from Modules.Bot.New_Menu.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from Modules.Shared.Query import getUsers


class SendMessageAll(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = ["send_message_to_everyone", "acquire_message", "done"]

        self.message_to_sent = ""

        self.INTRO_MESSAGES = {
            "send_message_to_everyone": "Dimmi pure il messaggio da inviare a tutti 😊",
        }

        self.KEYBOARDS = {
            "acquire_message": InlineKeyboardMarkup(
            [[InlineKeyboardButton("✔ Conferma", callback_data='confirm_message_to_sent')],
             [InlineKeyboardButton("🔙 Torna indietro", callback_data='main_admin')]])
        }


    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch
        await query.edit_message_text(self.INTRO_MESSAGES[current_batch])

    async def acquire_conversation_param(self, context: ContextTypes.DEFAULT_TYPE, previous_batch: str,
                                         current_batch: str, next_batch: str, chat_id: int, message_id: int,
                                         typed_string: str, flag: bool = None, entities=None):
        query = self.query
        self.message_to_sent = self.reconstruct_message_with_markdown(typed_string, entities)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await query.edit_message_text(text=f"Sicuro di voler confermare?\n{typed_string}",
                                      reply_markup=self.KEYBOARDS[current_batch])

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
        users = getUsers()
        ids_utenti = []
        for user in users:
            if str(str(user).split(" ")[3]).split(".")[0] == "Auletta":
                continue
            ids_utenti.append(str(user).split(" ")[0])
        for id_telegram in ids_utenti:
            await context.bot.send_message(chat_id=id_telegram,
                                           text=self.message_to_sent, parse_mode=ParseMode.MARKDOWN_V2)
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Ritorna al menu admin", callback_data='main_admin')]])
        await query.edit_message_text("La parola di Dio è stata diffusa!", reply_markup=keyboard)
        self.current_batch = ""

    def reconstruct_message_with_markdown(self, text: str, entities) -> str:
        formatted_text = ""
        last_offset = 0

        for entity in entities:
            formatted_text += self.escape_markdown_v2(text[last_offset:entity.offset])

            entity_text = self.escape_markdown_v2(text[entity.offset:entity.offset + entity.length])

            if entity.type == 'bold':
                formatted_text += f"*{entity_text}*"
            elif entity.type == 'italic':
                formatted_text += f"_{entity_text}_"
            elif entity.type == 'code':
                formatted_text += f"`{entity_text}`"

            last_offset = entity.offset + entity.length

        formatted_text += self.escape_markdown_v2(text[last_offset:])

        return formatted_text

    @staticmethod
    def escape_markdown_v2(text: str) -> str:
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
