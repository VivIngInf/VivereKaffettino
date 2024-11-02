from sqlalchemy.exc import NoResultFound
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from Modules.Shared.Query import (GetAulette, GetIdGruppiTelegramAdmin,
                                  GetIdTelegram, GetIsAdmin, GetIsVerified,
                                  GetMyAuletta, GetUnverifiedUsers, removeUser, CheckCardExists, GetVerifiedUsers,
                                  GetProdottiNonAssociati, GetIDProdotto, GetProdotti)

from Modules.Bot.Stop import stop, stop_to_restart_again
from Modules.Bot.UserInfo import Info
from Modules.Bot.Resoconti import SendUsersResoconto
from Modules.Bot.ShowBalance import ShowBalance
from Modules.Bot.History import History
from Modules.Bot.Start import Start
from Modules.Bot.Utility import *
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

    if "Admin" not in context.user_data and GetIsAdmin(str(query.message.chat_id)):
        text = "Sei stato promosso ad Admin, riavvia il Bot per aggiornarsi 😃.\nPremi /start e ricominciamooo!! 😊"
        # Tolgo lo stato iniziale dal dizionario
        if "first_start" in context.user_data:
            context.user_data.pop("first_start")
            await context.bot.edit_message_text(chat_id=query.message.chat_id,
                                                message_id=context.user_data["initial_message"].message_id,
                                                text=text)
            for _class in CONVERSATION_CLASSES:
                if _class in context.user_data:
                    context.user_data.pop(_class)

            context.user_data.pop("initial_message")
            return ConversationHandler.END

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

        case "history":
            await History(update, context)

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

        ##### ADMIN MENU #####

        case "main_admin":
            delete_all_conversations(context)
            await context.user_data["Admin"].start_conversation(update=None, context=context, query=query,
                                                                current_batch="main_admin")

        ##### CHANGE CARD #####

        case "change_card":
            context.user_data["ConversationManager"].set_active_conversation("ChangeCard")
            await context.user_data["ChangeCard"].start_conversation(update=None, context=context, query=query,
                                                                     current_batch="change_card")

        case "acquire_card_to_change":
            await context.user_data["ChangeCard"].forward_conversation(query, context, current_batch="acquire_card")

        case "change_card_done":
            await context.user_data["ChangeCard"].end_conversation(update=update, context=context, query=query)

        ##### MANAGE CARD MENU #####

        case "manage_card":
            delete_all_conversations(context)
            await context.user_data["ManageCard"].start_conversation(update=None, context=context, query=query,
                                                                     current_batch="manage_card")

        case "activate_card":
            context.user_data["ConversationManager"].set_active_conversation("ActivateCard")
            await context.user_data["ActivateCard"].start_conversation(update=None, context=context, query=query,
                                                                       current_batch="activate_card")
        case "activate_user":
            await context.user_data["ActivateCard"].end_conversation(update=update, context=context, query=query)

        case "deactivate_card":
            context.user_data["ConversationManager"].set_active_conversation("DeactivateCard")
            await context.user_data["DeactivateCard"].start_conversation(update=None, context=context, query=query,
                                                                         current_batch="deactivate_card")

        case selected_user if selected_user in {utente[0] for utente in
                                                GetVerifiedUsers(GetMyAuletta(query.from_user.id))}:
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Conferma", callback_data='deactivate_user')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='deactivate_card')]])
            context.user_data["DeactivateCard"].set_user_to_deactivate(selected_user)
            await query.edit_message_text(f"Hai scelto {selected_user}, confermi?", reply_markup=keyboard)

        case "deactivate_user":
            await context.user_data["DeactivateCard"].end_conversation(update=update, context=context, query=query)

        ##### VERIFY USER #####

        case "verify_user":
            context.user_data["ConversationManager"].set_active_conversation("VerifyUser")
            await context.user_data["VerifyUser"].start_conversation(update=None, context=context, query=query,
                                                                     current_batch="verify_user")

        case selected_user if selected_user in {utente[0] for utente in
                                                GetUnverifiedUsers(GetMyAuletta(query.from_user.id))}:

            # This case is shared with the activate_card, since both use
            # the buttons generates from UnverifiedUsers
            active_conversation = context.user_data["ConversationManager"].get_active_conversation()
            current_batch = context.user_data["ConversationManager"].get_current_conversation_batch(context)
            conversation_id = safe_hash_name(active_conversation, current_batch)
            if conversation_id == ACQUIRE_USERNAME_TO_ACTIVATE:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✔ Conferma", callback_data='activate_user')],
                     [InlineKeyboardButton("🔙 Torna indietro", callback_data='activate_card')]])
                context.user_data["ActivateCard"].set_user_to_activate(selected_user)
                await query.edit_message_text(f"Hai scelto {selected_user}, confermi?", reply_markup=keyboard)

            else:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✔ Conferma", callback_data='action_to_apply')],
                     [InlineKeyboardButton("🔙 Torna indietro", callback_data='verify_user')]])
                context.user_data["VerifyUser"].set_user_to_verify(selected_user)
                await query.edit_message_text(f"Hai scelto {selected_user}, confermi?", reply_markup=keyboard)

        case "action_to_apply":
            await context.user_data["VerifyUser"].forward_conversation(query, context, current_batch="action_to_apply")

        case "acquire_card_number":
            await context.user_data["VerifyUser"].forward_conversation(query, context,
                                                                       current_batch="acquire_card_number")

        case "assign_card":
            await context.user_data["VerifyUser"].end_conversation(update=update, context=context, query=query)

        case "delete_user":
            await context.user_data["VerifyUser"].bad_ending_conversation(update=update, context=context, query=query)

        ##### USER HISTORY #####

        case "user_history":
            context.user_data["ConversationManager"].set_active_conversation("ViewHistory")
            await context.user_data["ViewHistory"].start_conversation(update=None, context=context, query=query,
                                                                      current_batch="user_history")

        case selected_user if selected_user in {utente[0] + "h" for utente in
                                                GetVerifiedUsers(GetMyAuletta(query.from_user.id))}:
            # Adding an 'h' at the end of the username so this make difference between other cases
            # of course, before passing to the function, we need to remove that 'h'
            await context.user_data["ViewHistory"].end_conversation(update=update, context=context)
            await History(update, context, "user_history", GetIdTelegram(selected_user[:-1]))

        ##### ADD ADMIN #####

        case "add_admin":
            context.user_data["ConversationManager"].set_active_conversation("AddAdmin")
            await context.user_data["AddAdmin"].start_conversation(update=None, context=context, query=query,
                                                                   current_batch="add_admin")

        ##### REMOVE ADMIN #####

        case "remove_admin":
            context.user_data["ConversationManager"].set_active_conversation("RemoveAdmin")
            await context.user_data["RemoveAdmin"].start_conversation(update=None, context=context, query=query,
                                                                      current_batch="remove_admin")

        ##### SEND RESOCONTO #####

        case "send_resoconto":
            await SendUsersResoconto(context)
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Torna al menu admin", callback_data='main_admin')]])
            await query.edit_message_text("Resoconto inviato", reply_markup=keyboard)

        ##### SEND MESSAGE TO EVERYONE #####

        case "send_message_to_everyone":
            context.user_data["ConversationManager"].set_active_conversation("SendMessageAll")
            await context.user_data["SendMessageAll"].start_conversation(update=None, context=context, query=query,
                                                                         current_batch="send_message_to_everyone")

        case "confirm_message_to_sent":
            await context.user_data["SendMessageAll"].end_conversation(update=update, context=context, query=query)

        ##### UNLIMITED USER #####

        case "unlimited_user":
            context.user_data["ConversationManager"].set_active_conversation("UnlimitedUser")
            await context.user_data["UnlimitedUser"].start_conversation(update=None, context=context, query=query,
                                                                        current_batch="unlimited_user")

        case "acquire_card_unlimited":
            await context.user_data["UnlimitedUser"].forward_conversation(query, context,
                                                                          current_batch="acquire_card_unlimited")

        case "confirm_data_unlimited":
            await context.user_data["UnlimitedUser"].forward_conversation(query, context,
                                                                          current_batch="confirm_data_unlimited")

        case "create_unlimited_user":
            await context.user_data["UnlimitedUser"].end_conversation(update=update, context=context, query=query)

        ##### STORAGE MENU #####

        case "main_storage":
            delete_all_conversations(context)
            await context.user_data["StorageMenu"].start_conversation(update=None, context=context, query=query,
                                                                      current_batch="main_storage")

        case "select_new_product":
            await context.user_data["NewProduct"].start_conversation(update=None, context=context, query=query,
                                                                     current_batch="select_new_product")

        case selected_product_to_add if selected_product_to_add in {prodotto.descrizione for prodotto in
                                                                    GetProdottiNonAssociati(
                                                                        GetMyAuletta(query.from_user.id))}:
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Conferma", callback_data='product_added')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='select_new_product')]])
            context.user_data["NewProduct"].set_product_to_store(selected_product_to_add)
            await query.edit_message_text(f"Hai scelto {selected_product_to_add}, confermi?",
                                          reply_markup=keyboard)

        case "custom_new_product_storage":
            context.user_data["ConversationManager"].set_active_conversation("NewProduct")
            await context.user_data["NewProduct"].forward_conversation(query, context,
                                                                       current_batch="custom_new_product_storage")

        case "acquire_price_product":
            context.user_data["ConversationManager"].set_active_conversation("NewProduct")
            await context.user_data["NewProduct"].forward_conversation(query, context,
                                                                       current_batch="acquire_price_product")

        case "product_added":
            await context.user_data["NewProduct"].end_conversation(update=update, context=context, query=query)

        case "remove_product_storage":
            await context.user_data["RemoveProduct"].start_conversation(update=None, context=context, query=query,
                                                                        current_batch="remove_product_storage")

        case selected_product_to_remove if selected_product_to_remove in {prodotto.descrizione for prodotto in
                                                                          GetProdotti(
                                                                              GetMyAuletta(query.from_user.id))}:
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("✔ Conferma", callback_data='remove_done')],
                 [InlineKeyboardButton("🔙 Torna indietro", callback_data='remove_product_storage')]])
            context.user_data["RemoveProduct"].set_product_to_remove(selected_product_to_remove)
            await query.edit_message_text(f"Hai scelto {selected_product_to_remove}, confermi?",
                                          reply_markup=keyboard)

        case "remove_done":
            await context.user_data["RemoveProduct"].end_conversation(update=update, context=context, query=query)

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

    # print("##################")
    # print(active_conversation, current_batch)
    # print("##################")

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
        valid_number, is_negative, converted_amount = validate_string_to_float(amount)
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

    elif conversation_id == ACQUIRE_USERNAME_VERIFY:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        admin_user_is_valid = GetIdTelegram(username) != "None"
        admin_can_verify_user = username not in [user[0] for user in GetUnverifiedUsers(GetMyAuletta(chat_id))]
        await context.user_data["VerifyUser"].acquire_conversation_param(context,
                                                                         previous_batch="verify_user",
                                                                         current_batch="acquire_username",
                                                                         next_batch="action_to_apply",
                                                                         chat_id=chat_id,
                                                                         message_id=message_id,
                                                                         typed_string=username,
                                                                         flag=admin_user_is_valid,
                                                                         flag2=admin_can_verify_user)
    elif conversation_id == ACQUIRE_CARD_NUMBER:
        idCard = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        card_number_not_exist = not CheckCardExists(idCard)
        is_string = not idCard.isdigit()
        await context.user_data["VerifyUser"].acquire_conversation_param(context,
                                                                         previous_batch="action_to_apply",
                                                                         current_batch="acquire_card_number",
                                                                         next_batch="assign_card",
                                                                         chat_id=chat_id,
                                                                         message_id=message_id,
                                                                         typed_string=idCard,
                                                                         flag=card_number_not_exist,
                                                                         flag2=is_string)

    elif conversation_id == ACQUIRE_USERNAME_ADD_ADMIN:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        user_is_valid = GetIdTelegram(username=username) != "None"
        user_is_admin = False
        if user_is_valid:
            user_is_admin = GetIsAdmin(GetIdTelegram(username=username))
        await context.user_data["AddAdmin"].acquire_conversation_param(context,
                                                                       previous_batch="add_admin",
                                                                       current_batch="acquire_username",
                                                                       next_batch="done",
                                                                       chat_id=chat_id,
                                                                       message_id=message_id,
                                                                       typed_string=username,
                                                                       flag=user_is_valid,
                                                                       flag2=user_is_admin)
    elif conversation_id == ACQUIRE_USERNAME_REMOVE_ADMIN:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        user_is_valid = GetIdTelegram(username=username) != "None"
        user_is_user = False
        if user_is_valid:
            user_is_user = not GetIsAdmin(GetIdTelegram(username=username))
        await context.user_data["RemoveAdmin"].acquire_conversation_param(context,
                                                                          previous_batch="remove_admin",
                                                                          current_batch="acquire_username",
                                                                          next_batch="done",
                                                                          chat_id=chat_id,
                                                                          message_id=message_id,
                                                                          typed_string=username,
                                                                          flag=user_is_valid,
                                                                          flag2=user_is_user)

    elif conversation_id == ACQUIRE_MESSAGE_TO_SEND_ALL:
        message_to_sent = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        entities = update.message.entities
        await context.user_data["SendMessageAll"].acquire_conversation_param(context,
                                                                             previous_batch="send_message_to_everyone",
                                                                             current_batch="acquire_message",
                                                                             next_batch="done",
                                                                             chat_id=chat_id,
                                                                             message_id=message_id,
                                                                             typed_string=message_to_sent,
                                                                             entities=entities)

    elif conversation_id == ACQUIRE_USERNAME_CARD_CHANGE:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        user_is_invalid = not GetIdTelegram(username) != "None"
        await context.user_data["ChangeCard"].acquire_conversation_param(context,
                                                                         previous_batch="change_card",
                                                                         current_batch="acquire_username",
                                                                         next_batch="acquire_card_number",
                                                                         chat_id=chat_id,
                                                                         message_id=message_id,
                                                                         typed_string=username,
                                                                         flag=True,
                                                                         flag2=user_is_invalid)
    elif conversation_id == ACQUIRE_CARD_NUMBER_CHANGE:
        idCard = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        card_number_not_exist = not CheckCardExists(idCard)
        is_string = not idCard.isdigit()
        await context.user_data["ChangeCard"].acquire_conversation_param(context,
                                                                         previous_batch="acquire_username",
                                                                         current_batch="acquire_card_number",
                                                                         next_batch="change_card_done",
                                                                         chat_id=chat_id,
                                                                         message_id=message_id,
                                                                         typed_string=idCard,
                                                                         flag=card_number_not_exist,
                                                                         flag2=is_string)

    elif conversation_id == ACQUIRE_NEW_PRODUCT:
        product_name = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        product_name_not_exist = check_product(product_name)
        await context.user_data["NewProduct"].acquire_conversation_param(context,
                                                                         previous_batch="main_storage",
                                                                         current_batch="acquire_product",
                                                                         next_batch="acquire_price",
                                                                         chat_id=chat_id,
                                                                         message_id=message_id,
                                                                         typed_string=product_name,
                                                                         flag=product_name_not_exist,
                                                                         flag2=False)
    elif conversation_id == ACQUIRE_PRICE_PRODUCT:
        price_product = str(update.message.text).replace(",", ".")
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        valid_number, is_negative, converted_price = validate_string_to_float(price_product)
        await context.user_data["NewProduct"].acquire_conversation_param(context,
                                                                         previous_batch="acquire_product",
                                                                         current_batch="acquire_price",
                                                                         next_batch="product_added",
                                                                         chat_id=chat_id,
                                                                         message_id=message_id,
                                                                         typed_string="",
                                                                         typed_num=converted_price,
                                                                         flag=valid_number,
                                                                         flag2=is_negative)

    elif conversation_id == ACQUIRE_USERNAME_UNLIMITED:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await context.user_data["UnlimitedUser"].acquire_conversation_param(context,
                                                                            previous_batch="unlimited_user",
                                                                            current_batch="acquire_username",
                                                                            next_batch="acquire_card",
                                                                            chat_id=chat_id,
                                                                            message_id=message_id,
                                                                            typed_string=username,
                                                                            flag=True,
                                                                            flag2=False)
    elif conversation_id == ACQUIRE_CARD_UNLIMITED:
        idCard = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        card_number_not_exist = not CheckCardExists(idCard)
        is_string = not idCard.isdigit()
        await context.user_data["UnlimitedUser"].acquire_conversation_param(context,
                                                                            previous_batch="acquire_username",
                                                                            current_batch="acquire_card",
                                                                            next_batch="secure_confirm",
                                                                            chat_id=chat_id,
                                                                            message_id=message_id,
                                                                            typed_string=idCard,
                                                                            flag=card_number_not_exist,
                                                                            flag2=is_string)

    elif conversation_id == ACQUIRE_USERNAME_HISTORY:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        user_is_valid = GetIdTelegram(username=username) != "None"
        user_isnt_same_auletta_as_admin = GetMyAuletta(chat_id) != GetMyAuletta(
            int(GetIdTelegram(username))) if user_is_valid else False
        await context.user_data["ViewHistory"].acquire_conversation_param(context,
                                                                          previous_batch="user_history",
                                                                          current_batch="acquire_username",
                                                                          next_batch="history_done",
                                                                          chat_id=chat_id,
                                                                          message_id=message_id,
                                                                          typed_string=username,
                                                                          flag=user_is_valid,
                                                                          flag2=user_isnt_same_auletta_as_admin)

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


def validate_string_to_float(amount: str) -> [bool, bool, float]:
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


def check_product(product_name: str) -> bool:
    product_name_not_exist = True
    try:
        ID = GetIDProdotto(nomeProdotto=product_name)
        product_name_not_exist = False
    except NoResultFound:
        product_name_not_exist = True
    return product_name_not_exist


def check_regex_username(username: str) -> bool:
    """Controlla se l'username dell'utente rispetta lo standard Unipa 'Nome.Cognome{int}{int}' """
    pattern = r"^[A-Z][a-z-A-Z]+\.[A-Z][a-z-A-Z]+(([1-9][1-9])|0[1-9]|[1-9]0)?$"
    return re.match(pattern, username)


def check_regex_age(age: str) -> bool:
    """Controlla se l'età inserita ha il formato corretto"""
    pattern = r"^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/((19|20)\d\d)$"
    return re.match(pattern, age)
