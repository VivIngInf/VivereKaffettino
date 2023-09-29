from telegram import Update
from telegram.ext import ContextTypes
from TelegramBot.DatabaseHandler import GetUsername, CheckUserExists

async def Info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """USER_INFO: Permette all'utente di vedere il suo ID_Telegram ed il suo Username"""

    # Controlliamo se l'utente esiste, altrimenti non potremmo vedere il saldo
    if(not CheckUserExists(idTelegram=update.effective_chat.id)):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Non hai ancora un account!\nFai /add!")
        return None

    telegramID = update.effective_chat.id
    username = GetUsername(telegramID)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Il tuo ID_Telegram è: {telegramID}.\nIl tuo username è: {username}.")

    return None