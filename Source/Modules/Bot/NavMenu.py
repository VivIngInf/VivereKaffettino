import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from Modules.Bot.States import *
from ..Shared.Query import GetIdTelegram, CheckUsernameExists, GetIsVerified, GetIsAdmin
from Modules.Shared.Query import InsertUser, GetAulette, incrementaSaldo, SetAdminDB, InsertUser, GetUsername, assignCard
from Modules.Bot.ShowBalance import ShowBalance
from Modules.Bot.Start import Start
from Modules.Bot.Stop import Stop
from Modules.Bot.UserInfo import Info
import re


async def button_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ogni qual volta viene premuto un bottone del menù"""

    if list(context.user_data.keys()).count("first_start") == 0:
        context.user_data['first_start'] = False

    query = update.callback_query

    if query.data == 'back_main_menu':
        # Interrompo eventuali conversazioni in corso
        for action in ACTIONS:
            if list(context.user_data.keys()).count(action) > 0:
                context.user_data.pop(action)
        await Start(update, context)

    elif query.data == 'stop':
        # Interrompo eventuali conversazioni in corso
        for action in ACTIONS:
            if list(context.user_data.keys()).count(action) > 0:
                context.user_data.pop(action)
        await Stop(update, context)

    elif query.data == "registra":
        context.user_data['typing_username_registra'] = query
        buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Digita l'username rispettando lo stardard Unipa con iniziali grandi.\nEs: Massimo.Midiri03",
                                      reply_markup=keyboard)

    elif query.data == "selecting_auletta_registra":
        buttons = []
        for auletta in GetAulette():
            auletta = str(auletta).split()
            button = InlineKeyboardButton(text=auletta[1], callback_data=auletta[1])
            buttons.append([button])

        buttons.append([InlineKeyboardButton("❌ Annulla", callback_data='registra')])
        keyboard = InlineKeyboardMarkup(buttons)

        await query.edit_message_text(text=f"Car* {context.user_data['username']} seleziona la tua Auletta di appartenenza",
                                      reply_markup=keyboard)

    elif query.data in [str(auletta).split()[1] for auletta in GetAulette()]:
        InsertUser(context.user_data["username_id"], context.user_data["username"])
        buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(
            text=f"Carissim* {context.user_data['username']} benvenuto in Vivere Kaffettino! ✌",
            reply_markup=keyboard)
        context.user_data.pop("username")
        context.user_data.pop("username_id")

    elif query.data == 'saldo':
        await ShowBalance(update, context)

    elif query.data == 'ricarica':
        context.user_data['typing_username_ricarica'] = query
        buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Digita l'username", reply_markup=keyboard)

    elif query.data == "admin":
        buttons = [[InlineKeyboardButton("Verifica Utente ☑", callback_data='verify_user')],
                   [InlineKeyboardButton("Aggiungi Admin 🟢", callback_data='add_admin')],
                   [InlineKeyboardButton("Rimuovi Admin 🔴", callback_data='remove_admin')],
                   [InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Scegli cosa fare :)", reply_markup=keyboard)

    elif query.data == "add_admin":
        context.user_data['typing_add_admin'] = query
        buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='admin')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Digita l'username dell'utente da far diventare admin", reply_markup=keyboard)

    elif query.data == "remove_admin":
        context.user_data['typing_remove_admin'] = query
        buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='admin')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Digita l'username dell'utente da rimuovere dagli admin", reply_markup=keyboard)

    elif query.data == "verify_user":
        context.user_data['typing_verify_user'] = query
        buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Digita l'username dell'utente da far abilitare", reply_markup=keyboard)

    elif query.data == "typing_card":
        context.user_data["typing_card"] = query
        buttons = [[InlineKeyboardButton("🔙 Torna indietro all'username", callback_data='verify_user')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Digita l'ID CARD da assegnare all'utente", reply_markup=keyboard)

    elif query.data == "storage":
        # TODO: Sotto menu per lo storage e relative comunicazioni con il DB
        buttons = [[InlineKeyboardButton("Visualizza magazzino 🗄", callback_data='see_storage')],
                   [InlineKeyboardButton("Incrementa scorta 🟩", callback_data='add_storage')],
                   [InlineKeyboardButton("Rimuovi Prodotto 🟥", callback_data='remove_storage')],
                   [InlineKeyboardButton("Aggiungi Prodotto ➕", callback_data='new_storage')],
                   [InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Scegli cosa fare :)", reply_markup=keyboard)

    elif query.data == 'info':
        await Info(update, context)


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quando viene scritto qualcosa in chat"""

    if list(context.user_data.keys()).count("typing_username_registra") > 0:
        username = update.message.text
        if check_regex(username):
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            buttons = [[InlineKeyboardButton("✔ Conferma", callback_data='selecting_auletta_registra')],
                        [InlineKeyboardButton("❌ Annulla", callback_data='registra')]]
            keyboard = InlineKeyboardMarkup(buttons)
            query = context.user_data["typing_username_registra"]
            context.user_data["selecting_auletta_registra"] = query
            context.user_data["username"] = username
            context.user_data["username_id"] = update.message.chat_id
            await query.edit_message_text(text=f"Hai scritto {username}, confermi?", reply_markup=keyboard)
            context.user_data.pop("typing_username_registra")
        else:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            query = context.user_data["typing_username_registra"]
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"Hai digitato un username che non rispetta lo stardard Unipa, riprova.\nEs: Massimo.Midiri03",
                                          reply_markup=keyboard)

    elif list(context.user_data.keys()).count("typing_username_ricarica") > 0:
        username = update.message.text
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

        buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        query = context.user_data["typing_username_ricarica"]
        if GetIdTelegram(username=username) != "None":
            context.user_data["typing_amount_ricarica"] = query
            context.user_data["username"] = username
            await query.edit_message_text(text="Digita l'importo da ricaricare", reply_markup=keyboard)
            context.user_data.pop("typing_username_ricarica")
        else:
            await query.edit_message_text(text="Utente non trovato riprova oppure ritorna al menu principale", reply_markup=keyboard)

    elif list(context.user_data.keys()).count("typing_amount_ricarica") > 0:
        amount = update.message.text
        query = context.user_data["typing_amount_ricarica"]
        try:
            amount = float(amount)
        except ValueError:
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            await query.edit_message_text(text="Inserire un importo numerico valido!",
                                          reply_markup=keyboard)
        else:
            if amount <= 0:
                buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
                keyboard = InlineKeyboardMarkup(buttons)
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
                await query.edit_message_text(text="La ricarica deve essere positiva!",
                                              reply_markup=keyboard)
            else:
                buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
                keyboard = InlineKeyboardMarkup(buttons)
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
                incrementaSaldo(context.user_data['username'], amount)
                await query.edit_message_text(text=f"Ricarica a {context.user_data['username']} effettuata, torna pure al menu principale",
                                              reply_markup=keyboard)
                context.user_data.pop("typing_amount_ricarica")
                context.user_data.pop("username")

    elif list(context.user_data.keys()).count("typing_add_admin") > 0:
        username = update.message.text
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        query = context.user_data["typing_add_admin"]
        if GetIdTelegram(username=username) != "None":
            if GetIsAdmin(GetIdTelegram(username=username)):
                buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
                keyboard = InlineKeyboardMarkup(buttons)
                await query.edit_message_text(text=f"L'utente {username} è già un Admin",
                                              reply_markup=keyboard)
                context.user_data.pop("typing_add_admin")
            else:
                SetAdminDB(GetIdTelegram(username=username), True)
                buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
                keyboard = InlineKeyboardMarkup(buttons)
                await query.edit_message_text(text=f"Ok, l'utente {username} è stato promosso ad Admin", reply_markup=keyboard)
                context.user_data.pop("typing_add_admin")
        else:
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='admin')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text="Utente non trovato riprova oppure annulla",
                                          reply_markup=keyboard)

    elif list(context.user_data.keys()).count("typing_remove_admin") > 0:
        username = update.message.text
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        query = context.user_data["typing_remove_admin"]
        if GetIdTelegram(username=username) != "None":
            SetAdminDB(GetIdTelegram(username=username), False)
            buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text=f"Ok, l'utente {username} è stato tolto dagli Admin",
                                          reply_markup=keyboard)
            context.user_data.pop("typing_remove_admin")
        else:
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='admin')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text="Utente non trovato riprova oppure annulla",
                                          reply_markup=keyboard)

    elif list(context.user_data.keys()).count("typing_verify_user") > 0:
        username = update.message.text
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        query = context.user_data["typing_verify_user"]

        if GetIdTelegram(username) != "None":
            buttons = [[InlineKeyboardButton("✔ Conferma", callback_data='typing_card')],
                        [InlineKeyboardButton("❌ Annulla", callback_data='verify_user')]]
            keyboard = InlineKeyboardMarkup(buttons)
            context.user_data["username"] = username
            await query.edit_message_text(text=f"Sicuro di voler confermare {username}?", reply_markup=keyboard)
            context.user_data.pop("typing_verify_user")
        else:
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text="Utente non trovato, riprova o ritorna al menu principale",
                                          reply_markup=keyboard)

    elif list(context.user_data.keys()).count("typing_card") > 0:
        idCard = update.message.text
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        query = context.user_data["typing_card"]

        if idCard.isdigit():
            buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            assignCard(GetIdTelegram(context.user_data['username']), idCard)
            await query.edit_message_text(text=f"L'utente {context.user_data['username']} è stato verificato correttamente!",
                                          reply_markup=keyboard)
            context.user_data.pop("typing_card")
            context.user_data.pop("username")
        else:
            buttons = [[InlineKeyboardButton("🔙 Torna indietro all'username", callback_data='verify_user')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text="ID CARD non valido, inserire un valore strettamente numerico!",
                                          reply_markup=keyboard)

    else:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)



def check_regex(username: str) -> bool:
    """Controlla se l'username dell'utente rispetta lo standard Unipa 'Nome.Cognome{int}{int}' """
    pattern = r"^[A-Z][a-z-A-Z]+\.[A-Z][a-z-A-Z]+(([1-9][1-9])|0[1-9]|[1-9]0)?$"
    return re.match(pattern, username)

