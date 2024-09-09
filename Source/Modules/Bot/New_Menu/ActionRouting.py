from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from Modules.Shared.Query import (CheckUsernameExists, GetAuletta, GetAulette, GetIdGruppiTelegramAdmin,
                                  GetIdGruppoTelegram, GetIdGruppoTelegram, GetIdTelegram, GetIsAdmin, GetIsVerified,
                                  GetMyAuletta, GetNomeAuletta, GetUnverifiedUsers, GetUsername, InsertUser,
                                  InsertUser, SetAdminDB, SetIsVerified, assignCard, getGender, getIDCard, getUsers,
                                  incrementaSaldo, removeUser)

from Modules.Bot.New_Menu.Stop import stop, stop_after_registration, stop_command, stop_to_restart_again
from Modules.Bot.New_Menu.UserInfo import Info
from Modules.Bot.Resoconti import SendUsersResoconto
from Modules.Bot.New_Menu.ShowBalance import ShowBalance
from Modules.Bot.New_Menu.Start import Start
from Modules.Bot.New_Menu.Utility import *
import re


async def button_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Every time a button has been pressed"""

    query = update.callback_query

    if "ConversationManager" not in context.user_data:
        message_id = query.message.message_id
        chat_id = query.message.chat_id
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Il Bot si è riavviato per aggiornarsi 😃.\nPremi /start e ricominciamooo!! 😊"
        )
        return

    if "first_start" in context.user_data:
        context.user_data['first_start'] = False

    # active_conversation = context.user_data["ConversationManager"].get_active_conversation()
    # current_batch = context.user_data["ConversationManager"].get_current_conversation_batch(context)
    # print("##################")
    # print(active_conversation, current_batch)
    # print("##################")

    match query.data:

        case 'back_main_menu':
            delete_all_conversations(context)
            await Start().start_conversation(update, context)

        case 'stop':
            delete_all_conversations_and_manager(context)
            await stop(update, context)

        case "info":
            await Info(update, context)

        case "delete_request_registration_account":
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Conferma",
                                       callback_data='remove_and_restart_registration_again')],
                 [InlineKeyboardButton("❌ Annulla",
                                       callback_data='back_main_menu')]])
            await query.edit_message_text(
                f"Sei sicuro di voler annullare la registrazione? Ti perderai il nostro buonissimo Kaffè 😤",
                reply_markup=keyboard)

        case "remove_and_restart_registration_again":
            removeUser(str(query.from_user.id))
            delete_all_conversations_and_manager(context)
            await stop_to_restart_again(update, context)

        case 'balance':
            await ShowBalance(update, context)

        ##### REGISTRATION #####

        case "register":
            context.user_data["ConversationManager"].set_active_conversation("Registration")
            await context.user_data["Registration"].start_conversation(update=None, context=context, query=query,
                                                                       current_batch="acquire_username")

        case "acquire_age":
            await context.user_data["Registration"].forward_conversation(query, context, current_batch="acquire_age")

        case "select_gender":
            await context.user_data["Registration"].forward_conversation(query, context, current_batch="select_gender")

        case gender_selezionato if gender_selezionato in {'donna', 'uomo', 'altro'}:
            await context.user_data["Registration"].forward_conversation(query, context, current_batch="confirm_gender")

        case "select_auletta":
            await context.user_data["Registration"].forward_conversation(query, context, current_batch="select_auletta")

        case auletta_selezionata if auletta_selezionata in {str(auletta).split()[1] for auletta in GetAulette()}:
            await context.user_data["Registration"].end_conversation(update=update, context=context, query=query)

        ##### RECHARGE #####

        case "recharge":
            context.user_data["ConversationManager"].set_active_conversation("Recharge")
            await context.user_data["Recharge"].start_conversation(update=None, context=context, query=query,
                                                                       current_batch="acquire_username")

        case "recharge_done":
            await context.user_data["Recharge"].end_conversation(update=update, context=context, query=query)


        case _:
            try:
                # (azione proveniente dal gruppo degli admin)
                action = str(query.data).split(":")[0]
                username = str(query.data).split(":")[1]

                if GetIsVerified(GetIdTelegram(username)):
                    await query.edit_message_text(text=f"L'utente {username} è già stato verificato!")
                else:
                    if action == "instant_delete":
                        removeUser(GetIdTelegram(username))
                        await query.edit_message_text(text=f"L'utente {username} è stato rimosso correttamente!")

                    elif action == "instant_verify":
                        keyboard = InlineKeyboardMarkup(
                            [[InlineKeyboardButton("Procedi sul Bot", url=f"https://t.me/{context.bot.username}")]])
                        await query.edit_message_text(
                            text=f"Ottimo! Procedi alla verifica direttamente dalla chat privata",
                            reply_markup=keyboard)
            except IndexError:
                pass


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Every time something is typed"""
    active_conversation = context.user_data["ConversationManager"].get_active_conversation()
    current_batch = context.user_data["ConversationManager"].get_current_conversation_batch(context)

    print("##################")
    print(active_conversation, current_batch)
    print("##################")

    conversation_id = safe_hash_name(active_conversation, current_batch)

    if conversation_id == ACQUIRE_USERNAME_REGISTRATION:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        valid_username = check_regex_username(username)
        await context.user_data["Registration"].acquire_conversation_param(context,
                                                                           previous_batch="register",
                                                                           current_batch="acquire_username",
                                                                           next_batch="acquire_age",
                                                                           chat_id=chat_id,
                                                                           message_id=message_id,
                                                                           typed_string=username,
                                                                           flag=valid_username)
    elif conversation_id == ACQUIRE_AGE_REGISTRATION:
        age = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        valid_age = check_regex_age(age)
        await context.user_data["Registration"].acquire_conversation_param(context,
                                                                           previous_batch="acquire_username",
                                                                           current_batch="acquire_age",
                                                                           next_batch="select_gender",
                                                                           chat_id=chat_id,
                                                                           message_id=message_id,
                                                                           typed_string=age,
                                                                           flag=valid_age)

    elif conversation_id == ACQUIRE_USERNAME_RECHARGE:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        user_is_valid = GetIdTelegram(username=username) != "None"
        user_exist = GetIdTelegram(username=username) == str(chat_id)
        await context.user_data["Recharge"].acquire_conversation_param(context,
                                                                       previous_batch="recharge",
                                                                       current_batch="acquire_username",
                                                                       next_batch="acquire_amount",
                                                                       chat_id=chat_id,
                                                                       message_id=message_id,
                                                                       typed_string=username,
                                                                       flag=user_is_valid,
                                                                       flag2=user_exist)
    elif conversation_id == ACQUIRE_AMOUNT_RECHARGE:
        amount = str(update.message.text).replace(",", ".")
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        valid_number, is_negative, converted_amount = validate_amount(amount)
        await context.user_data["Recharge"].acquire_conversation_param(context,
                                                                       previous_batch="acquire_username",
                                                                       current_batch="acquire_amount",
                                                                       next_batch="recharge_done",
                                                                       chat_id=chat_id,
                                                                       message_id=message_id,
                                                                       typed_string="",
                                                                       typed_num=converted_amount,
                                                                       flag=valid_number,
                                                                       flag2=is_negative)


    else:
        # I messaggi vengono eliminati solo se al di fuori dei gruppi degli admin
        IdGroups = [item[0] for item in GetIdGruppiTelegramAdmin() if item[0] is not None]
        if str(update.message.chat_id) not in IdGroups:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)


def delete_all_conversations(context: ContextTypes.DEFAULT_TYPE):
    """Every time user goes to main menu, the conversation manager will be empty automatically"""
    context.user_data["ConversationManager"].set_active_conversation('')


def delete_all_conversations_and_manager(context: ContextTypes.DEFAULT_TYPE):
    """User for stop the Bot"""
    for _class in CONVERSATION_CLASSES:
        if _class in context.user_data:
            context.user_data.pop(_class)


def validate_amount(amount: str) -> [bool, bool, float]:
    """Support function for validate amount to charge"""
    valid_number = False
    is_negative = True
    converted_amount = 0.
    try:
        converted_amount = float(amount)
        valid_number = True
    except ValueError:
        pass
    else:
        if converted_amount > 0:
            is_negative = False
    return valid_number, is_negative, converted_amount


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
