from telegram.ext import  CallbackContext
from ..Shared.Configs import GetChannelID
from ..Shared.Query import getOperazioniGiornaliere
import pandas
from io import BytesIO
from datetime import datetime

async def SendResoconto(context: CallbackContext):

    columns = ['ID_Operazione', 'ID_Telegram', 'ID_Auletta', 'ID_Prodotto', 'DateTimeOperazione', 'Costo']

    rows = getOperazioniGiornaliere()
    print(rows)

    # Creazione del DataFrame
    df = pandas.DataFrame(rows, columns=columns)

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)  # Riposiziona il cursore all'inizio del buffer

    await context.bot.send_document(chat_id=f"{GetChannelID()}", document=excel_buffer, filename='operazioni_excel.xlsx', caption=f"Resoconto del {datetime.date()} inviato!")