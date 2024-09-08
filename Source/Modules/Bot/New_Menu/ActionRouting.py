from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from Modules.Shared.Query import (CheckUsernameExists, GetAuletta, GetAulette, GetIdGruppiTelegramAdmin,
                                  GetIdGruppoTelegram, GetIdGruppoTelegram, GetIdTelegram, GetIsAdmin, GetIsVerified,
                                  GetMyAuletta, GetNomeAuletta, GetUnverifiedUsers, GetUsername, InsertUser,
                                  InsertUser, SetAdminDB, SetIsVerified, assignCard, getGender, getIDCard, getUsers,
                                  incrementaSaldo, removeUser)

from Stop import stop, stop_after_registration, stop_command, stop_to_restart_again
from UserInfo import Info
from Modules.Bot.Resoconti import SendUsersResoconto
from ShowBalance import ShowBalance
from Start import Start
from Utility import *
import re


async def button_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Every time a button has been pressed"""

    if "first_start" in context.user_data:
        context.user_data['first_start'] = False

    query = update.callback_query

    match query.data:

        case 'back_main_menu':
            delete_all_conversations(context)
            await Start().start_conversation(update, context)

        case 'stop':
            delete_all_conversations(context)
            await stop(update, context)

        case "info":
            await Info(update, context)

        case "delete_request_registration_account":
            keyboard = InlineKeyboardMarkup(
                            [[InlineKeyboardButton("✔ Conferma", callback_data='remove_and_restart_registration_again')],
                            [InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]])
            await query.edit_message_text(
                f"Sei sicuro di voler annullare la registrazione? Ti perderai il nostro buonissimo Kaffè 😤",
                reply_markup=keyboard)

        case "remove_and_restart_registration_again":
            removeUser(str(query.from_user.id))
            delete_all_conversations(context)
            await stop_to_restart_again(update, context)

        case 'saldo':
            await ShowBalance(update, context)

        ##### START REGISTRATION #####

        case "register":
            context.user_data["ConversationManager"].set_active_conversation("Registration")
            await context.user_data["Registration"].start_conversation(query, context)

        case "acquire_age":
            await context.user_data["Registration"].forward_conversation(query, context, current_batch="acquire_age")

        case "select_gender":
            await context.user_data["Registration"].forward_conversation(query, context, current_batch="select_gender")

        case gender_selezionato if gender_selezionato in {'donna', 'uomo', 'altro'}:
            await context.user_data["Registration"].forward_conversation(query, context, current_batch="confirm_gender")

        case "select_auletta":
            await context.user_data["Registration"].forward_conversation(query, context, current_batch="select_auletta")

        case auletta_selezionata if auletta_selezionata in {str(auletta).split()[1] for auletta in GetAulette()}:
            await context.user_data["Registration"].end_conversation()
            context.user_data["ConversationManager"].set_active_conversation("")

        ##### END REGISTRATION #####


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Every time something is typed"""

    match context.user_data["ConversationManager"].get_current_conversation_batch():

        case "acquire_username":
            username = update.message.text
            chat_id = update.message.chat_id
            message_id = update.message.message_id
            flag = check_regex_username(username)
            await context.user_data["Registration"].acquire_conversation_param(context,
                                                                               previous_batch="register",
                                                                               current_batch="acquire_username",
                                                                               next_batch="acquire_age",
                                                                               chat_id=chat_id,
                                                                               message_id=message_id,
                                                                               typed_string=username,
                                                                               flag=flag)
        case "acquire_age":
            age = update.message.text
            chat_id = update.message.chat_id
            message_id = update.message.message_id
            flag = check_regex_age(age)
            await context.user_data["Registration"].acquire_conversation_param(context,
                                                                               previous_batch="acquire_username",
                                                                               current_batch="acquire_age",
                                                                               next_batch="select_gender",
                                                                               chat_id=chat_id,
                                                                               message_id=message_id,
                                                                               typed_string=age,
                                                                               flag=flag)

        case _:
            print(update.message.chat_id)
            # I messaggi vengono eliminati solo se al di fuori dei gruppi degli admin
            IdGroups = [item[0] for item in GetIdGruppiTelegramAdmin() if item[0] is not None]
            if str(update.message.chat_id) not in IdGroups:
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)


def delete_all_conversations(context: ContextTypes.DEFAULT_TYPE):
    for _class in CONVERSATION_CLASSES:
        if _class in context.user_data:
            context.user_data.pop(_class)

def check_regex_username(username: str) -> bool:
    """Controlla se l'username dell'utente rispetta lo standard Unipa 'Nome.Cognome{int}{int}' """
    pattern = r"^[A-Z][a-z-A-Z]+\.[A-Z][a-z-A-Z]+(([1-9][1-9])|0[1-9]|[1-9]0)?$"
    return re.match(pattern, username)


def check_regex_age(age: str) -> bool:
    """Controlla se l'età inserita ha il formato corretto"""
    pattern = r"^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/((19|20)\d\d)$"
    return re.match(pattern, age)


def reconstruct_message_with_markdown(text, entities):
    formatted_text = ""
    last_offset = 0

    for entity in entities:
        formatted_text += escape_markdown_v2(text[last_offset:entity.offset])

        entity_text = escape_markdown_v2(text[entity.offset:entity.offset + entity.length])

        if entity.type == 'bold':
            formatted_text += f"*{entity_text}*"
        elif entity.type == 'italic':
            formatted_text += f"_{entity_text}_"
        elif entity.type == 'code':
            formatted_text += f"`{entity_text}`"
        # Add handling for other entity types if necessary

        last_offset = entity.offset + entity.length

    formatted_text += escape_markdown_v2(text[last_offset:])

    return formatted_text


def escape_markdown_v2(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
