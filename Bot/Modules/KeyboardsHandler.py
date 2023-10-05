from telegram import Update, CallbackQuery
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from Modules.AddUser import AddUserKeyboardHandler
from Modules.ShowBalance import ShowBalance

async def KeyboardAulette(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQuery, data: int) -> None: 
    
    AddUserKeyboardHandler(update=update, context=context, idAuletta=data)
    await query.edit_message_text(text=f"Hai selezionato: {data}")
    return None

async def KeyboardSaldo(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler, data: int) -> None:

    ShowBalance(update=update, context=context)
    await query.edit_message_text(text=f"Hai selezionato: {data}")
    return None

async def KeyBoardHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:    

    query = update.callback_query

    await query.answer()

    qSplit : str

    if ":" in query.data:
        qSplit = query.data.split(":")
        flag = qSplit[0]
        data = qSplit[1]
    else:
        flag = query.data

    match flag:
        case "SAL":
            KeyboardSaldo(update=update, context=context, query=query, data=data)

        case "Auletta":
            KeyboardAulette(update=update, context=context, data=data, query=query)

    return None
