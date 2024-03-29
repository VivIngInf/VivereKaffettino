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

    print(rows)

    for row in rows:
        tempArr = []
        dTime = ""
        valori = str(row).split(" ")
        for v in valori:
            if str(v).find("-") != -1:
                dTime += v
                continue
            elif str(v).find(":") != -1:
                dTime += v
                tempArr.append(dTime)
            else:
                tempArr.append(v)
        rowsDataframe.append(tempArr)

    # Creazione del DataFrame
    df = pandas.DataFrame(rowsDataframe, columns=columns)

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)  # Riposiziona il cursore all'inizio del buffer

    await context.bot.send_document(chat_id=f"{GetChannelID()}", document=excel_buffer, filename=f'Resoconto-{datetime.date(datetime.now())}.xlsx', caption=f"Resoconto del {datetime.date(datetime.now())} inviato!")