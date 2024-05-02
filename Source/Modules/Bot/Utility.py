from telegram import InlineKeyboardButton

# Azioni attive durante le conversazioni
ACTIONS = ["acquire_username_toregister", "acquire_age", "dataNascita", "selecting_gender", "gender",
           "selecting_auletta_registra", "auletta",
           "acquire_amount_tocharge", "validate_amount_tocharge",
           "acquire_user_tomake_admin", "acquire_user_toremove_from_admin", "acquire_card_number",
           "acquire_user_toverify", "change_card", "acquire_card_to_change", "idCard_tochange", "acquire_user_to_change_card", "acquire_user_toverify_keyboard", "action_to_perform",
           "username", "username_id", "idCard", "chat_id", "message_id", "amount"]

GENDER_DICT = {"donna": "a", "uomo": "o", "altro": "ə"}
DB_GENDER_DICT = {"D": "a", "U": "o", "A": "ə"}

buttons_dict = {
    "back_main_menu": [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]],

    "correct_acquire_username_toregister": [[InlineKeyboardButton("✔ Conferma", callback_data='age')],
                                         [InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]],

    "wrong_acquire_username_toregister": [[InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]],

    "correct_acquire_age": [[InlineKeyboardButton("✔ Conferma", callback_data='selecting_gender')],
                            [InlineKeyboardButton("🔙 Torna indietro", callback_data='age')]],

    "selecting_gender": [[InlineKeyboardButton("Donna", callback_data='donna')],
                           [InlineKeyboardButton("Uomo", callback_data='uomo')],
                           [InlineKeyboardButton("Altro", callback_data='altro')],
                           [InlineKeyboardButton("🔙 Torna indietro", callback_data='age')]],

    "done_selecting_gender": [[InlineKeyboardButton("✔️ Conferma", callback_data='selecting_auletta_registra')],
                           [InlineKeyboardButton("🔙 Torna indietro", callback_data='selecting_gender')]],

    "validate_amount_tocharge": [[InlineKeyboardButton("✔ Conferma", callback_data='done_ricarica')],
                    [InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]],

    "acquire_card_number": [[InlineKeyboardButton("✔ Conferma", callback_data='acquired_card')],
                                         [InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]],

    "instant_acquire_card_number": [[InlineKeyboardButton("✔ Conferma", callback_data='instant_acquired_card')],
                                             [InlineKeyboardButton("❌ Annulla", callback_data='back_main_menu')]],

    "admin": [[InlineKeyboardButton("Verifica Utente ☑", callback_data='acquire_user_toverify')],
               [InlineKeyboardButton("Cambia Tessera 🔄", callback_data='change_card')],
               [InlineKeyboardButton("Aggiungi Admin 🟢", callback_data='add_admin')],
               [InlineKeyboardButton("Rimuovi Admin 🔴", callback_data='remove_admin')],
               [InlineKeyboardButton("Resoconto Utenti Excel 📃", callback_data='send_resoconto')],
               [InlineKeyboardButton("🔙 Ritorna al menu principale", callback_data='back_main_menu')]]
}

