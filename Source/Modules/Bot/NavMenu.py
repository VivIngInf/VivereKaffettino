from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from Modules.Bot.Utility import *
from Modules.Shared.Query import InsertUser, GetAulette, incrementaSaldo, SetAdminDB, \
    InsertUser, GetUsername, assignCard, SetIsVerified, \
    GetIdTelegram, CheckUsernameExists, GetIsVerified, GetIsAdmin, \
    getGender, GetUnverifiedUsers, GetIdGruppoTelegram, GetMyAuletta, removeUser, GetIdGruppoTelegram, GetAuletta, \
    GetIdGruppiTelegramAdmin, getIDCard, GetNomeAuletta, getUsers
from Modules.Bot.ShowBalance import ShowBalance
from Modules.Bot.Start import Start
from Modules.Bot.Stop import Stop, Stop_after_registration, Stop_command, Stop_torestart_again
from Modules.Bot.UserInfo import Info
from Modules.Bot.Resoconti import SendUsersResoconto
import re


async def button_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ogni qual volta viene premuto un bottone del menù"""

    if "first_start" in context.user_data:
        context.user_data['first_start'] = False

    query = update.callback_query

    match query.data:

        case 'back_main_menu':
            # Interrompo eventuali conversazioni in corso
            for action in ACTIONS:
                if action in context.user_data:
                    context.user_data.pop(action)
            await Start(update, context)

        case 'stop':
            # Interrompo eventuali conversazioni in corso
            for action in ACTIONS:
                if action in context.user_data:
                    context.user_data.pop(action)
            await Stop(update, context)

        case "info":
            await Info(update, context)


        case "ask_for_restart_again":
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✔ Conferma", callback_data='remove_and_restart_again')],
                        [InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]])
            await query.edit_message_text(
                f"Sei sicuro di voler annullare la registrazione? Ti perderai il nostro buonissimo Kaffè 😤",
                reply_markup=keyboard)

        case "remove_and_restart_again":
            removeUser(query.from_user.id)
            for action in ACTIONS:
                if action in context.user_data:
                    context.user_data.pop(action)

            await Stop_torestart_again(update, context)

        case 'saldo':
            await ShowBalance(update, context)

        case "registra":
            # Elimino l'eventuale conversazione nel caso premo il bottone per tornare indietro
            if "acquire_age" in context.user_data:
                context.user_data.pop('acquire_age')
            # Creo una nuova conversazione
            context.user_data['acquire_username_toregister'] = query
            keyboard = InlineKeyboardMarkup(buttons_dict["back_main_menu"])
            await query.edit_message_text(
                f"Digita l'username rispettando lo stardard Unipa con iniziali grandi.\nEs: Massimo.Midiri03",
                reply_markup=keyboard)

        case "age":
            # Elimino l'eventuale conversazione nel caso premo il bottone per tornare indietro
            if "gender" in context.user_data:
                context.user_data.pop('gender')
            # Creo una nuova conversazione
            context.user_data["acquire_age"] = query
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Torna indietro", callback_data='registra')]])
            await query.edit_message_text(
                f"Digita la tua data di nascita rispettando il formato dell'esempio per favore.\nEs: 11/09/2001",
                reply_markup=keyboard)

        case "selecting_gender":
            # Elimino l'eventuale conversazione nel caso premo il bottone per tornare indietro
            if "gender" in context.user_data:
                context.user_data.pop('gender')
            # Creo una nuova conversazione
            keyboard = InlineKeyboardMarkup(buttons_dict["selecting_gender"])
            await query.edit_message_text(text=f"Adesso seleziona il tuo genere per favore", reply_markup=keyboard)

        case gender_selezionato if gender_selezionato in {'donna', 'uomo', 'altro'}:
            keyboard = InlineKeyboardMarkup(buttons_dict["done_selecting_gender"])
            context.user_data["gender"] = query.data
            await query.edit_message_text(text=f"Hai selezionato {query.data.upper()}, confermi?",
                                          reply_markup=keyboard)

        case "selecting_auletta_registra":
            buttons = []
            for auletta in GetAulette():
                auletta = str(auletta).split()
                button = InlineKeyboardButton(text=auletta[1], callback_data=auletta[1])
                buttons.append([button])
            buttons.append([InlineKeyboardButton("🔙 Torna indietro", callback_data='selecting_gender')])
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text=f"Seleziona la tua Auletta di appartenenza",
                                          reply_markup=keyboard)

        case auletta_selezionata if auletta_selezionata in {str(auletta).split()[1] for auletta in GetAulette()}:
            context.user_data["auletta"] = query.data
            await Inserisci_Utente(context)
            buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(
                text=f"{context.user_data['username']} benvenut{GENDER_DICT[context.user_data['gender']]} in Vivere Kaffettino!",
                reply_markup=keyboard)
            context.user_data.pop("username")
            context.user_data.pop("username_id")
            context.user_data.pop("gender")
            context.user_data.pop("dataNascita")
            context.user_data.pop("auletta")

            for action in ACTIONS:
                if action in context.user_data:
                    context.user_data.pop(action)
            await Stop_after_registration(update, context)

        case 'ricarica':
            context.user_data['acquire_user_tocharge'] = query
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"Digita l'username dell'utente che vuole ricaricare", reply_markup=keyboard)

        case "done_ricarica":
            buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)

            incrementaSaldo(usernameBeneficiario=context.user_data['username'], IDTelegramAmministratore=query.from_user.id, ricarica=context.user_data["amount"])

            await query.edit_message_text(
                text=f"Ricarica a {context.user_data['username']} effettuata!\nTorna pure al menu principale",
                reply_markup=keyboard)

            await context.bot.send_message(chat_id=GetIdTelegram(context.user_data['username']),
                                           text=f'Ciao {context.user_data["username"]}, ricarica di {context.user_data["amount"]} effettuata grazie e goditi i tuoi caffè! :)')

            context.user_data.pop("validate_amount_tocharge")
            context.user_data.pop("username")
            context.user_data.pop("amount")

        case "admin":
            keyboard = InlineKeyboardMarkup(buttons_dict["admin"])
            await query.edit_message_text(f"GESTIONE ADMIN", reply_markup=keyboard)

        case "change_card":
            # Elimino l'eventuale conversazione nel caso premo il bottone per tornare indietro
            if "acquire_card_to_change" in context.user_data:
                context.user_data.pop('acquire_card_to_change')
            context.user_data['acquire_user_to_change_card'] = query
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"Digita l'username dell'utente di cui cambiare l'ID CARD", reply_markup=keyboard)

        case "acquire_card_to_change":
            context.user_data['acquire_card_to_change'] = query
            buttons = [[InlineKeyboardButton("🔙 Torna Indietro", callback_data='change_card')]]
            keyboard = InlineKeyboardMarkup(buttons)
            if getIDCard(GetIdTelegram(context.user_data['username'])) == 0:
                await query.edit_message_text(
                    f"Non è assegnato alcun ID CARD al momento.\nDigita il nuovo ID CARD",
                    reply_markup=keyboard)
            else:
                await query.edit_message_text(f"Il vecchio ID CARD è {getIDCard(GetIdTelegram(context.user_data['username']))}.\nDigita il nuovo ID CARD", reply_markup=keyboard)


        case "perform_card_change":
            assignCard(GetIdTelegram(context.user_data["username"]), context.user_data["idCard_tochange"])
            buttons = [[InlineKeyboardButton("🔙 Torna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(
                f"Adesso l'ID CARD è {context.user_data['idCard_tochange']}",
                reply_markup=keyboard)

        case "add_admin":
            context.user_data['acquire_user_tomake_admin'] = query
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='admin')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"Digita l'username dell'utente da far diventare admin",
                                          reply_markup=keyboard)

        case "remove_admin":
            context.user_data['acquire_user_toremove_from_admin'] = query
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='admin')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"Digita l'username dell'utente da rimuovere dagli admin",
                                          reply_markup=keyboard)

        case "send_resoconto":
            await SendUsersResoconto(context)
            buttons = [[InlineKeyboardButton("🔙 Torna al menu admin", callback_data='admin')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"Resoconto inviato",
                                          reply_markup=keyboard)

        case "send_message_toeveryone":
            context.user_data['acquire_message_tosent'] = query
            await query.edit_message_text(f"Dimmi pure il messaggio da inviare a tutti 😊")

        case "confirm_message_tosent":
            users = getUsers()
            ids_utenti = []
            for user in users:
                if str(str(user).split(" ")[3]).split(".")[0] == "Auletta":
                    continue
                ids_utenti.append(str(user).split(" ")[0])

            for id_telegram in ids_utenti:
                await context.bot.send_message(chat_id=id_telegram,
                                               text=context.user_data["message_tosent"], parse_mode=ParseMode.MARKDOWN_V2)
            context.user_data.pop("message_tosent")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Ritorna al menu admin", callback_data='admin')]])
            await query.edit_message_text(f"La parola di Dio è stata diffusa!", reply_markup=keyboard)

        case "acquire_user_toverify":
            buttons = list()
            admin_who_makes_the_query = query.from_user.id
            for utente in GetUnverifiedUsers(GetMyAuletta(admin_who_makes_the_query)):
                button = InlineKeyboardButton(text=utente[0], callback_data=utente[0])
                buttons.append([button])
            buttons.append([InlineKeyboardButton("🔙 Torna indietro", callback_data='admin')])
            keyboard = InlineKeyboardMarkup(buttons)
            if len(buttons) == 1:
                await query.edit_message_text(f"Non ci sono utenti da verificare", reply_markup=keyboard)
            else:
                context.user_data["acquire_user_toverify"] = query
                context.user_data["acquire_user_toverify_keyboard"] = keyboard
                await query.edit_message_text(
                    f"Scegli chi abilitare tramite i bottoni oppure scrivi il nome utente in chat",
                    reply_markup=keyboard)

        case utente_selezionato if utente_selezionato in {utente[0] for utente in
                                                          GetUnverifiedUsers(GetMyAuletta(query.from_user.id))}:
            for ACTION in ("acquire_user_toverify", "acquire_user_toverify_keyboard"):
                if ACTION in context.user_data:
                    context.user_data.pop(ACTION)

            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✔ Conferma", callback_data='action_to_perform')],
                                             [InlineKeyboardButton("🔙 Torna indietro",
                                                                   callback_data='acquire_user_toverify')]])

            await query.edit_message_text(f"Hai scelto {utente_selezionato}, confermi?", reply_markup=keyboard)
            context.user_data["user_toverify"] = utente_selezionato

        case "action_to_perform":
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✔ Verifica", callback_data='acquire_card_number')],
                                             [InlineKeyboardButton("✖ Elimina", callback_data='delete_user')],
                                             [InlineKeyboardButton("🔙 Torna indietro",
                                                                   callback_data='acquire_user_toverify')]])

            await query.edit_message_text(f"Cosa vuoi fare?", reply_markup=keyboard)

        case "delete_user":
            removeUser(GetIdTelegram(context.user_data["user_toverify"]))
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Torna indietro", callback_data='acquire_user_toverify')]])
            await query.edit_message_text(
                text=f"L'utente {context.user_data['user_toverify']} è stato rimosso correttamente!",
                reply_markup=keyboard)
            for ACTION in ("acquire_user_toverify", "acquire_user_toverify_keyboard", "user_toverify"):
                if ACTION in context.user_data:
                    context.user_data.pop(ACTION)

        case "acquire_card_number":
            context.user_data["acquire_card_number"] = query
            buttons = [[InlineKeyboardButton("🔙 Torna indietro", callback_data='action_to_perform')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"Digita l'ID CARD da assegnare all'utente", reply_markup=keyboard)

        case "acquired_card":
            # Completa la verifica dell'utente una volta inserito il numero della CARD
            assignCard(GetIdTelegram(context.user_data['user_toverify']), context.user_data['idCard'])
            idTelegram = GetIdTelegram(username=context.user_data['user_toverify'])
            gender = getGender(idTelegram=idTelegram)

            SetIsVerified(GetIdTelegram(context.user_data["user_toverify"]))

            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Ritorna al menu admin", callback_data='admin')]])
            await query.edit_message_text(
                text=f"L'utente {context.user_data['user_toverify']} è stato verificato correttamente!",
                reply_markup=keyboard)
            # Avviso l'utente che è stato verificato
            await context.bot.send_message(chat_id=GetIdTelegram(context.user_data['user_toverify']),
                                           text=f'{context.user_data["user_toverify"]}, sei stat{DB_GENDER_DICT[gender]} abilitat{DB_GENDER_DICT[gender]} ad usare Vivere Kaffettino.\n\nVieni in auletta per ritirare la card!\n\nPremi /start per iniziare e goditi i tuoi caffè! :)')
            context.user_data.pop("acquire_card_number")
            context.user_data.pop("idCard")
            context.user_data.pop("user_toverify")

        case "storage":
            # Elimino l'eventuale conversazione nel caso premo il bottone per tornare indietro
            if "acquire" in context.user_data:
                context.user_data.pop('nome_prodotto')
            # TODO: Sotto menu per lo storage e relative comunicazioni con il DB
            buttons = [[InlineKeyboardButton("Rimuovi Prodotto 🟥", callback_data='remove_storage')],
                       [InlineKeyboardButton("Aggiungi Prodotto ➕", callback_data='new_storage')],
                       [InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"GESTIONE MAGAZZINO", reply_markup=keyboard)

        case "new_storage":
            # Elimino l'eventuale conversazione nel caso premo il bottone per tornare indietro
            if "acquire_nome_prodotto" in context.user_data:
                context.user_data.pop('acquire_nome_prodotto')
            context.user_data["acquire_nome_prodotto"] = query
            username = query.from_user.first_name
            admin_who_makes_the_query = query.from_user.id
            auletta = GetNomeAuletta(GetMyAuletta(admin_who_makes_the_query))
            context.user_data["auletta_4storage"] = auletta
            buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"Ciao {username}, dimmi pure il prodotto da aggiungere nella tua Auletta ({auletta})", reply_markup=keyboard)

        case "remove_storage":
            # Funzione da implementare in futuro
            pass

        case "acquire_costo_prodotto":
            context.user_data["acquire_costo_prodotto"] = query
            buttons = [[InlineKeyboardButton("🔙 Torna indietro", callback_data='new_storage')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text("Ora dimmi quanto costa per favore", reply_markup=keyboard)

        case "confirm_new_prodotto":
            auletta = context.user_data["auletta_4storage"]
            nome_prodotto = context.user_data["nome_prodotto"]
            costo_prodotto = context.user_data["costo_prodotto"]
            # TODO: Query per l'aggiunta al DB
            context.user_data.pop("auletta_4storage")
            context.user_data.pop("nome_prodotto")
            context.user_data.pop("costo_prodotto")
            buttons = [[InlineKeyboardButton("🔙 Torna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(f"{nome_prodotto} al costo di {costo_prodotto}, aggiunto all'Auletta {auletta} correttamente!", reply_markup=keyboard)

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
                        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Procedi sul Bot", url=f"https://t.me/{context.bot.username}")]])
                        await query.edit_message_text(text=f"Ottimo! Procedi alla verifica direttamente dalla chat privata", reply_markup=keyboard)
            except IndexError:
                pass


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quando viene scritto qualcosa in chat"""

    if "acquire_username_toregister" in context.user_data:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_username_toregister(username, chat_id, message_id, context)


    elif "acquire_age" in context.user_data:
        age = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_age(age, chat_id, message_id, context)


    elif "acquire_user_tocharge" in context.user_data:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_user_tocharge(username, chat_id, message_id, context)


    elif "validate_amount_tocharge" in context.user_data:
        amount = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await validate_amount_tocharge(amount, chat_id, message_id, context)


    elif "acquire_user_tomake_admin" in context.user_data:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_user_tomake_admin(username, chat_id, message_id, context)


    elif "acquire_user_toremove_from_admin" in context.user_data:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_user_toremove_from_admin(username, chat_id, message_id, context)


    elif "acquire_user_toverify" in context.user_data:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_user_toverify(username, chat_id, message_id, context)

    elif "acquire_user_to_change_card" in context.user_data:
        username = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_user_to_change_card(username, chat_id, message_id, context)

    elif "acquire_card_to_change" in context.user_data:
        idCard = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_card_to_change(idCard, chat_id, message_id, context)

    elif "acquire_card_number" in context.user_data:
        idCard = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_card_number(idCard, chat_id, message_id, context)

    elif "acquire_nome_prodotto" in context.user_data:
        nome_prodotto = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_nome_prodotto(nome_prodotto, chat_id, message_id, context)

    elif "acquire_costo_prodotto" in context.user_data:
        costo_prodotto = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await acquire_costo_prodotto(costo_prodotto, chat_id, message_id, context)

    elif "acquire_message_tosent" in context.user_data:
        messaggio_da_inviare = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        entities = update.message.entities
        await acquire_message_tosent(messaggio_da_inviare, entities, chat_id, message_id, context)

    else:
        # I messaggi vengono eliminati solo se al di fuori dei gruppi degli admin
        IdGroups = [item[0] for item in GetIdGruppiTelegramAdmin() if item[0] is not None]
        if str(update.message.chat_id) not in IdGroups:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)


async def acquire_username_toregister(username: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    if check_regex_username(username):
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        keyboard = InlineKeyboardMarkup(buttons_dict["correct_acquire_username_toregister"])
        query = context.user_data["acquire_username_toregister"]
        context.user_data["username"] = username
        context.user_data["username_id"] = chat_id
        await query.edit_message_text(text=f"Hai scritto {username}, confermi?", reply_markup=keyboard)
        # Esco dalla conversazione
        context.user_data.pop("acquire_username_toregister")
    else:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        query = context.user_data["acquire_username_toregister"]
        keyboard = InlineKeyboardMarkup(buttons_dict["wrong_acquire_username_toregister"])
        await query.edit_message_text(
            f"Hai digitato un username che non rispetta lo stardard Unipa, riprova.\nEs: Massimo.Midiri03",
            reply_markup=keyboard)


async def acquire_age(age: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    if check_regex_age(age):
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        keyboard = InlineKeyboardMarkup(buttons_dict["correct_acquire_age"])
        query = context.user_data["acquire_age"]
        context.user_data["dataNascita"] = age
        await query.edit_message_text(text=f"Hai scritto {age}, confermi?", reply_markup=keyboard)
        # Esco dalla conversazione
        context.user_data.pop("acquire_age")
    else:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        query = context.user_data["acquire_age"]
        keyboard = InlineKeyboardMarkup(buttons_dict["back_main_menu"])
        await query.edit_message_text(
            f"Hai digitato una data di nascita che non rispetta lo stardard, riprova.\nEs: 11/09/2001",
            reply_markup=keyboard)


async def acquire_user_tocharge(username: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
    keyboard = InlineKeyboardMarkup(buttons)
    query = context.user_data["acquire_user_tocharge"]
    if GetIdTelegram(username=username) != "None":
        if GetIdTelegram(username=username) == str(chat_id):
            await query.edit_message_text(text="Sorry ma non puoi ricaricare te stesso, riprova oppure annulla e ritorna al menu principale", reply_markup=keyboard)
        else:
            context.user_data["validate_amount_tocharge"] = query
            context.user_data["username"] = username
            await query.edit_message_text(text="Digita l'importo da ricaricare", reply_markup=keyboard)
            context.user_data.pop("acquire_user_tocharge")
    else:
        await query.edit_message_text(text="Utente non trovato riprova oppure annulla e ritorna al menu principale",
                                      reply_markup=keyboard)


async def validate_amount_tocharge(amount: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    query = context.user_data["validate_amount_tocharge"]
    amount = amount.replace(",", ".")
    try:
        amount = float(amount)
    except ValueError:
        buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await query.edit_message_text(text="Inserire un importo numerico valido!",
                                      reply_markup=keyboard)
    else:
        if amount <= 0:
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await query.edit_message_text(text="La ricarica deve essere positiva!",
                                          reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup(buttons_dict["validate_amount_tocharge"])
            context.user_data["amount"] = amount
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await query.edit_message_text(text=f"Sicuro di voler confermare {amount}?", reply_markup=keyboard)
            context.user_data.pop("validate_amount_tocharge")


async def acquire_user_tomake_admin(username: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    query = context.user_data["acquire_user_tomake_admin"]
    if GetIdTelegram(username=username) != "None":
        if GetIsAdmin(GetIdTelegram(username=username)):
            buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text=f"L'utente {username} è già un Admin",
                                          reply_markup=keyboard)
            context.user_data.pop("acquire_user_tomake_admin")
        else:
            SetAdminDB(GetIdTelegram(username=username), True)
            buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text=f"Ok, l'utente {username} è stato promosso ad Admin",
                                          reply_markup=keyboard)
            context.user_data.pop("acquire_user_tomake_admin")
    else:
        buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='admin')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text="Utente non trovato riprova oppure annulla",
                                      reply_markup=keyboard)


async def acquire_user_toremove_from_admin(username: str, chat_id: int, message_id: int,
                                           context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    query = context.user_data["acquire_user_toremove_from_admin"]
    if GetIdTelegram(username=username) != "None":
        if GetIsAdmin(GetIdTelegram(username=username)):
            SetAdminDB(GetIdTelegram(username=username), False)
            buttons = [[InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text=f"Ok, l'utente {username} è stato tolto dagli Admin",
                                          reply_markup=keyboard)
            context.user_data.pop("acquire_user_toremove_from_admin")
        else:
            buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='admin')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text="L'utente non è un admin, riprova oppure annulla",
                                          reply_markup=keyboard)
    else:
        buttons = [[InlineKeyboardButton("❌ Annulla", callback_data='admin')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text="Utente non trovato riprova oppure annulla",
                                      reply_markup=keyboard)


async def acquire_user_toverify(username: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Acquisisco il nome utente che deve essere verificato"""
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    query = context.user_data["acquire_user_toverify"]

    if GetIdTelegram(username) != "None":
        if username not in [user[0] for user in GetUnverifiedUsers(GetMyAuletta(chat_id))]:
            query = context.user_data["acquire_user_toverify"]
            keyboard = context.user_data["acquire_user_toverify_keyboard"]
            await query.edit_message_text(
                text=f"Non sei abilitato ad attivare questo utente in quanto non appartiente alla tua Auletta.\nRiprova o seleziona l'utente con i bottoni",
                reply_markup=keyboard)
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        else:
            context.user_data.pop("acquire_user_toverify")
            context.user_data.pop("acquire_user_toverify_keyboard")
            buttons = [[InlineKeyboardButton("✔ Conferma", callback_data='action_to_perform')],
                       [InlineKeyboardButton("🔙 Torna indietro", callback_data='acquire_user_toverify')]]
            keyboard = InlineKeyboardMarkup(buttons)
            context.user_data["username"] = username
            await query.edit_message_text(text=f"Sicuro di voler confermare {username}?", reply_markup=keyboard)
    else:
        keyboard = context.user_data["acquire_user_toverify_keyboard"]
        await query.edit_message_text(text="Utente non trovato, riprova o seleziona l'utente con i bottoni",
                                      reply_markup=keyboard)


async def acquire_user_to_change_card(username: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Acquisisco il nome utente per cui deve essere cambiata la card"""
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    query = context.user_data["acquire_user_to_change_card"]

    if GetIdTelegram(username) != "None":
        context.user_data.pop("acquire_user_to_change_card")
        buttons = [[InlineKeyboardButton("✔ Conferma", callback_data='acquire_card_to_change')],
                   [InlineKeyboardButton("🔙 Torna indietro", callback_data='admin')]]
        keyboard = InlineKeyboardMarkup(buttons)
        context.user_data["username"] = username
        await query.edit_message_text(text=f"Sicuro di voler confermare {username}?", reply_markup=keyboard)
    else:
        buttons = [[InlineKeyboardButton("🔙 Torna indietro", callback_data='admin')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text="Utente non trovato, riprova o torna al menu admin",
                                      reply_markup=keyboard)


async def acquire_card_to_change(idCard: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Acquisisco il nuovo ID CARD"""
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    query = context.user_data["acquire_card_to_change"]

    try:
        int(idCard)
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Torna indietro", callback_data='change_card')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text="Inserisci un numero intero valido per favore!",
                                      reply_markup=keyboard)
    else:
        context.user_data.pop("acquire_card_to_change")
        buttons = [[InlineKeyboardButton("✔ Conferma", callback_data='perform_card_change')],
                   [InlineKeyboardButton("🔙 Torna indietro", callback_data='change_card')]]
        keyboard = InlineKeyboardMarkup(buttons)
        context.user_data["idCard_tochange"] = idCard
        await query.edit_message_text(text=f"Sicuro di voler confermare {idCard}?", reply_markup=keyboard)



async def acquire_card_number(idCard: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Acquisisco il numero della CARD"""
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    query = context.user_data["acquire_card_number"]

    if idCard.isdigit():
        keyboard = InlineKeyboardMarkup(buttons_dict["acquire_card_number"])
        context.user_data["idCard"] = idCard
        await query.edit_message_text(
            text=f"Sicuro di voler confermare {context.user_data['user_toverify']} con idCard: {idCard}?",
            reply_markup=keyboard)
    else:
        buttons = [[InlineKeyboardButton("🔙 Torna indietro all'username", callback_data='verify_user')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text="ID CARD non valido, inserire un valore strettamente numerico!",
                                      reply_markup=keyboard)



async def acquire_nome_prodotto(nome_prodotto: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Acquisisco il nuovo prodotto"""
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    query = context.user_data["acquire_nome_prodotto"]
    context.user_data.pop("acquire_nome_prodotto")
    buttons = [[InlineKeyboardButton("✔ Conferma", callback_data='acquire_costo_prodotto')],
               [InlineKeyboardButton("🔙 Torna indietro", callback_data='new_storage')]]
    keyboard = InlineKeyboardMarkup(buttons)
    context.user_data["nome_prodotto"] = nome_prodotto
    await query.edit_message_text(text=f"Sicuro di voler confermare {nome_prodotto}?", reply_markup=keyboard)


async def acquire_costo_prodotto(costo_prodotto: str, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    query = context.user_data["acquire_costo_prodotto"]
    costo_prodotto = costo_prodotto.replace(",", ".")
    try:
        costo_prodotto = float(costo_prodotto)
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Torna indietro", callback_data='new_storage')]]
        keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await query.edit_message_text(text="Inserire un importo numerico valido!",
                                      reply_markup=keyboard)
    else:
        if costo_prodotto <= 0:
            buttons = [[InlineKeyboardButton("🔙 Torna indietro", callback_data='new_storage')]]
            keyboard = InlineKeyboardMarkup(buttons)
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await query.edit_message_text(text="Il prezzo deve essere positivo!",
                                          reply_markup=keyboard)
        else:
            buttons = [[InlineKeyboardButton("✔ Conferma", callback_data='confirm_new_prodotto')],
                        [InlineKeyboardButton("🔙 Torna indietro", callback_data='new_storage')]]
            keyboard = InlineKeyboardMarkup(buttons)
            context.user_data["costo_prodotto"] = costo_prodotto
            context.user_data.pop("acquire_costo_prodotto")
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await query.edit_message_text(text=f"Sicuro di voler confermare {costo_prodotto}?", reply_markup=keyboard)


async def acquire_message_tosent(messaggio_da_inviare: str, entities, chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    query = context.user_data["acquire_message_tosent"]
    buttons = [[InlineKeyboardButton("✔ Conferma", callback_data='confirm_message_tosent')],
                [InlineKeyboardButton("🔙 Torna indietro", callback_data='admin')]]
    keyboard = InlineKeyboardMarkup(buttons)
    formatted_text = reconstruct_message_with_markdown(messaggio_da_inviare, entities)
    context.user_data["message_tosent"] = formatted_text
    context.user_data.pop("acquire_message_tosent")
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    await query.edit_message_text(text=f"Sicuro di voler confermare?\n{messaggio_da_inviare}", reply_markup=keyboard)



async def Inserisci_Utente(context: ContextTypes.DEFAULT_TYPE):
    """Memorizza nel DB e avvisa gli admin"""
    InsertUser(idTelegram=context.user_data["username_id"], auletta=context.user_data["auletta"],
               genere=convertToGenderDB(context.user_data["gender"]), dataNascita=context.user_data["dataNascita"],
               username=context.user_data["username"])
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✔ Verifica",
                                                           callback_data=f'instant_verify:{context.user_data["username"]}')],
                                     [InlineKeyboardButton("✖ Elimina",
                                                           callback_data=f'instant_delete:{context.user_data["username"]}')]])

    await context.bot.send_message(chat_id=GetIdGruppoTelegram(GetAuletta(context.user_data["auletta"])),
                                   text=f'Ciao ragazzi, {context.user_data["username"]} si è appena registrato',
                                   reply_markup=keyboard)


def check_regex_username(username: str) -> bool:
    """Controlla se l'username dell'utente rispetta lo standard Unipa 'Nome.Cognome{int}{int}' """
    pattern = r"^[A-Z][a-z-A-Z]+\.[A-Z][a-z-A-Z]+(([1-9][1-9])|0[1-9]|[1-9]0)?$"
    return re.match(pattern, username)


def check_regex_age(age: str) -> bool:
    """Controlla se l'età inserita ha il formato corretto"""
    pattern = r"^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/((19|20)\d\d)$"
    return re.match(pattern, age)


def convertToGenderDB(gender: str) -> str:
    """Ritorna solo la prima lettera del genere passato come parametro"""
    return gender[0].upper()


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

