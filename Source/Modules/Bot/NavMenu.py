from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from Modules.Bot.States import *
from ..Shared.Query import GetIdTelegram, CheckUsernameExists, GetIsVerified
from Modules.Shared.Query import InsertUser, GetAulette, incrementaSaldo
from Modules.Bot.ShowBalance import ShowBalance
from Modules.Bot.Start import Start
from Modules.Bot.Stop import Stop
from Modules.Bot.UserInfo import Info


async def button_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ogni qual volta viene premuto un bottone del menù"""

    query = update.callback_query

    if query.data == 'back_main_menu':
        # Interrompo eventuali conversazioni in corso
        for action in ACTIONS:
            if list(context.user_data.keys()).count(action) > 0:
                context.user_data.pop(action)
        context.user_data['state'] = MAIN_MENU
        await Start(update, context)

    elif query.data == 'stop':
        await Stop(update, context)

    elif query.data == 'saldo':
        await ShowBalance(update, context)

    elif query.data == 'ricarica':
        context.user_data['typing_username_ricarica'] = query
        buttons = [[InlineKeyboardButton("Annulla", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Digita l'username", reply_markup=keyboard)

    elif query.data == "admin":
        buttons = [[InlineKeyboardButton("Aggiungi Admin ➕", callback_data='add_admin')],
                   [InlineKeyboardButton("Remiovi Admin ➖", callback_data='remove_admin')],
                   [InlineKeyboardButton("Ritorna al menu principale", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Scegli cosa fare :)", reply_markup=keyboard)

    elif query.data == "add_admin":
        context.user_data['typing_add_admin'] = query
        buttons = [[InlineKeyboardButton("Annulla", callback_data='admin')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"Digita l'username dell'utente da far diventare admin", reply_markup=keyboard)

    elif query.data == 'info':
        await Info(update, context)


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quando viene scritto qualcosa in chat"""

    if list(context.user_data.keys()).count("typing_username_ricarica") > 0:
        username = update.message.text
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

        buttons = [[InlineKeyboardButton("Annulla", callback_data='back_main_menu')]]
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
        buttons = [[InlineKeyboardButton("Annulla", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        query = context.user_data["typing_amount_ricarica"]
        try:
            amount = float(amount)
        except ValueError:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            await query.edit_message_text(text="Inserire un importo numerico valido!",
                                          reply_markup=keyboard)
        else:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            incrementaSaldo(context.user_data['username'], amount)
            await query.edit_message_text(text=f"Ricarica a {context.user_data['username']} effettuata, torna pure al menu principale",
                                          reply_markup=keyboard)
            context.user_data.pop("typing_amount_ricarica")
            context.user_data.pop("username")

    elif list(context.user_data.keys()).count("typing_add_admin") > 0:
        username = update.message.text
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        buttons = [[InlineKeyboardButton("Annulla", callback_data='admin')]]
        keyboard = InlineKeyboardMarkup(buttons)
        query = context.user_data["typing_add_admin"]
        if GetIdTelegram(username=username) != "None":
            await query.edit_message_text(text=f"Ok, l'utente {username} è stato promosso ad Admin", reply_markup=keyboard)
            context.user_data.pop("typing_add_admin")
        else:
            await query.edit_message_text(text="Utente non trovato riprova oppure ritorna al menu principale",
                                          reply_markup=keyboard)
    else:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)