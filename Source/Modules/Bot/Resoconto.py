from telegram.ext import  CallbackContext
from ..Shared.Configs import GetChannelID
from ..Shared.Query import getOperazioniGiornaliere
import pandas
from io import BytesIO
from datetime import datetime

async def SendResoconto(context: CallbackContext):

    columns = ['ID_Operazione', 'ID_Telegram', 'ID_Auletta', 'ID_Prodotto', 'DateTimeOperazione', 'Costo']

    rows = getOperazioniGiornaliere()
    rowsDataframe = []

    for row in rows:
        valori = str(row).split(" ")
        rowsDataframe.append(valori)

    print(rowsDataframe)

    # Creazione del DataFrame
    df = pandas.DataFrame(rowsDataframe, columns=columns)

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)  # Riposiziona il cursore all'inizio del buffer

    await context.bot.send_document(chat_id=f"{GetChannelID()}", document=excel_buffer, filename=f'Resoconto-{datetime.date(datetime.now())}.xlsx', caption=f"Resoconto del {datetime.date(datetime.now())} inviato!")