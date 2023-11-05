from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from Modules.Bot.States import *
from Modules.Bot.Stop import Stop
from Modules.Bot.Start import Start
from Modules.Shared.Query import InsertUser, GetAulette

# TODO: SISTEMARE BOTTONI, FARE ARRIVARE CALLBACK DELL'AULETTA SCELTA, FILTRO USERNAME, FILTRO PAROLACCE

async def Register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Add information about yourself."""
    context.user_data[CURRENT_LEVEL] = SELF
    text = "Ottimo, iniziamo! 😁"

    button = InlineKeyboardButton(text="Daje", callback_data=str(SUCA))
    keyboard = InlineKeyboardMarkup.from_button(button)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return REGISTER

# -------------------

# Third level callbacks
async def select_feature(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select a feature to update for the person."""
    if not context.user_data.get(START_OVER):   
        context.user_data[FEATURES] = {MALE: update.callback_query.data}

    userData = context.user_data

    username = InlineKeyboardButton(text="Username", callback_data=str(USERNAME))
    auletta = InlineKeyboardButton(text="Auletta", callback_data=str(AULETTA))
    end = InlineKeyboardButton(text="Done", callback_data=str(END))

    buttons = []

    if USERNAME not in userData[FEATURES]:
        buttons.append([username])
    elif AULETTA not in userData[FEATURES]:
        # Mettiamo le aulette in riga
        aulette = GetAulette()
        for auletta in aulette:
            auletta = str(auletta).split()
            button = InlineKeyboardButton(text=auletta[1], callback_data=str(AULETTA))
            buttons.append([button])

    else:
        buttons.append([end])

    keyboard = InlineKeyboardMarkup(buttons)

    # If we collect features for a new person, clear the cache and save the gender
    if not context.user_data.get(START_OVER):
        text = "Inserisci l'username."

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = f"Scegli l'auletta."

        await update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE


async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Prompt user to input data for selected feature."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Ti ascolto."

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return TYPING


async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Save input for feature and return to feature selection."""
    user_data = context.user_data
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text

    user_data[START_OVER] = True

    return await select_feature(update, context)


async def end_describing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End gathering of features and return to parent conversation."""

    user_data = context.user_data

    InsertUser(idTelegram=update.effective_chat.id, username=user_data[FEATURES][USERNAME])

    level = user_data[CURRENT_LEVEL]
    if not user_data.get(level):
        user_data[level] = []
    user_data[level].append(user_data[FEATURES])

    # Print upper level menu
    if level == SELF:
        user_data[START_OVER] = True
        await Start(update, context)

    return END

# ------------

registerConv =  ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                select_feature, pattern="^" + str(SUCA) + "$"
            )
        ],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(ask_for_input, pattern="^(?!" + str(END) + ").*$")
            ],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_input)],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern="^" + str(END) + "$"),
            CommandHandler("stop", Stop),
        ],
        map_to_parent={
            # Return to second level menu
            END: SELECTING_LEVEL,
            # End conversation altogether
            STOPPING: STOPPING,
        },
    )