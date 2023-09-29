from telegram import Update
from telegram.ext import ContextTypes
from TelegramBot.DatabaseHandler import GetUsername

async def Info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """USER_INFO: Permette all'utente di vedere il suo ID_Telegram ed il suo Username"""

    telegramID = update.effective_chat.id
    username = GetUsername(telegramID)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Il tuo ID_Telegram è: {telegramID}.\nIl tuo username è: {username}.")

    return None