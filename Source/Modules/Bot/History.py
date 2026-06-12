from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from ..Shared.Query import getStoricoPersonale, GetUsername
from math import fsum


async def History(update: Update, context: ContextTypes.DEFAULT_TYPE, custom_callback: str = "back_main_menu",
                  customIdTelegram: str = None):
    """Manda come messaggio all'utente il suo storico a partire dall'ID_Telegram"""
    idTelegram = str(update.effective_chat.id)

    text = get_history(idTelegram) if customIdTelegram is None else get_history(customIdTelegram)

    buttons = [[InlineKeyboardButton("🔙 Torna indietro", callback_data=custom_callback)]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )


def get_history(idTelegram: str) -> str:
    storico, costoTotale = getStoricoPersonale(idTelegram)
    username = GetUsername(idTelegram)

    if not storico:
        text = f"🚫 {username}, non ci sono operazioni disponibili nello storico 🚫"
    else:
        formatted_history = "\n".join(
            f"• **{op.dateTimeOperazione.strftime('%d-%m-%Y')}** --> {op.costo}€"
            for op in storico
        )
        costoParziale = fsum(op.costo for op in storico)
        text = (
            f"📜 **Storico di {username}**:\n\n"
            f"{formatted_history}\n\n"
            f"**Totale mostrate ({len(storico)})**: {costoParziale}€\n"
            f"**Totale generale**: {costoTotale:.2f}€"
        )
    return text
