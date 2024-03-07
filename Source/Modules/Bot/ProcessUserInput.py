from telegram import Update
from telegram.ext import ContextTypes
from Modules.Bot.States import *
from Modules.Bot.Start import Start
from ..Shared.Query import GetIdTelegram, CheckUserExists, GetIsVerified

async def ProcessUserInput(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Gestisco tutti i messaggi in arrivo"""

    sub_menu = context.user_data["conversation"][0]

    match sub_menu:
        case None:
            print("Menu Principale")
            pass
        case "ricarica":
            username: str = update.message.text
            idTelegram = GetIdTelegram(username=username)
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            if idTelegram == "None":
                await context.user_data["conversation"][1].edit_message_text(text=f"Non esiste un utente con username: {username}\nRiprova oppure fai /cancel")
                return USERNAME

            # Se l'utente non è verificato allora annulla
            elif not GetIsVerified(idTelegram=idTelegram):
                await context.user_data["conversation"][1].edit_message_text(text="L'utente non è stato ancora verificato")
                return MAINMENU
            else:
                # await context.bot.edit_message_text(message_id=update.message.message_id,
                await context.user_data["conversation"][1].edit_message_text(text=f"Utente scritto {username}")
        case 1:
            pass

    # print("CIAOOOASCIASOAC", context.user_data, SELECTING_LEVEL)


    # context.user_data[START_OVER] = False
    # return SELECTING_ACTION


async def recharge_inputs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {MALE: update.callback_query.data}

    userData = context.user_data

    buttons = []

    if AULETTA not in userData[FEATURES]:
        # Mettiamo le aulette in riga
        aulette = GetAulette()
        for auletta in aulette:
            auletta = str(auletta).split()
            button = InlineKeyboardButton(text=auletta[1], callback_data=str(AULETTA))
            buttons.append([button])
    else:
        buttons.append([end])


    if not context.user_data.get(START_OVER):
        text = "Inserisci l'username :)"

        # await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = f"Scegli l'auletta."

        await update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE
