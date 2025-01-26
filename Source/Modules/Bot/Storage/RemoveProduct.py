from Modules.Bot.SubMenu import SubMenu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Modules.Shared.Query import GetNomeAuletta, GetMyAuletta, AssegnaProdotto, GetProdottiNonAssociati, \
    GetIDProdotto, GetAuletta, QuantitaECosto, GetIdGruppoTelegram, GetUsername, GetProdotti


class RemoveProduct(SubMenu):

    def __init__(self):
        super().__init__()

        # conversation_batches = []

        self.product_params = {

            "auletta": "",

            "acquire_product": "",

        }

        self.INTRO_MESSAGES = {

            "remove_product_storage": "Seleziona il prodotto da rimuovere dalla lista di seguito",

        }

        self.KEYBOARDS = {

            "remove_product_storage": InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Ritorna al menu magazzino", callback_data='main_storage')]]),
        }

    def set_product_to_remove(self, product_to_remove: str):
        self.product_params["acquire_product"] = product_to_remove

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None,
                                 current_batch: str = None):
        self.query = query
        self.current_batch = current_batch
        username = query.from_user.first_name
        admin_who_makes_the_query = query.from_user.id
        auletta = GetNomeAuletta(GetMyAuletta(admin_who_makes_the_query))
        self.product_params["auletta"] = auletta

        buttons = []
        for prodotto in GetProdotti(GetMyAuletta(admin_who_makes_the_query)):
            if prodotto.isVisible:
                button = InlineKeyboardButton(text=prodotto.descrizione, callback_data=prodotto.descrizione)
                buttons.append([button])

        buttons.append([InlineKeyboardButton("🔙 Torna indietro", callback_data='main_storage')])
        self.UNREGISTERED_PRODUCTS = InlineKeyboardMarkup(buttons)
        if len(buttons) > 1:
            await query.edit_message_text(f"Ciao {username}, di seguito trovi tutti i prodotti presenti nella "
                                          f"tua Auletta ({auletta}).\n"
                                          f"Seleziona uno di essi per rimuoverlo 😊",
                                          reply_markup=self.UNREGISTERED_PRODUCTS)
        else:
            await query.edit_message_text(f"Ciao {username}, la tua Auletta ({auletta})"
                                          f" non ha prodotti da rimuovere 😊",
                                          reply_markup=self.UNREGISTERED_PRODUCTS)

    async def end_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
        auletta = self.product_params["auletta"]
        product_name = self.product_params["acquire_product"]
        product_price = QuantitaECosto(GetIDProdotto(product_name), GetAuletta(auletta=auletta)).costo

        AssegnaProdotto(nomeAuletta=auletta, nomeProdotto=product_name, costo=product_price, isVisible=False)

        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Torna al menu magazzino",
                                                               callback_data='main_storage')]])
        await query.edit_message_text(
            f"{product_name} rimosso all'Auletta {auletta} correttamente!",
            reply_markup=keyboard)

        await context.bot.send_message(chat_id=GetIdGruppoTelegram(GetAuletta(auletta)),
                                       text=f'Ciao ragazzi, {GetUsername(query.from_user.id)} ha rimosso un prodotto '
                                            f'avente i seguenti dati\n'
                                            f"Nome -> {product_name}\n"
                                            f"Prezzo   -> {product_price}\n"
                                            f"Auletta  -> {auletta}")

        self.current_batch = ""
