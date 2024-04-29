from telegram.ext import  CallbackContext
from ..Shared.Configs import GetChannelID
from ..Shared.Query import getOperazioniGiornaliere, GetUsersExcel
import pandas
from io import BytesIO
from datetime import datetime

# TODO: Fare il join nel resoconto giornaliero con Utente, Auletta e Prodotto:
#       Fargli visualizzare Username, NomeAuletta, NomeProdotto, DateTimeOperazione, Costo

async def SendDailyResoconto(context: CallbackContext):

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


async def SendUsersResoconto(context: CallbackContext):
    
    columns = ['ID_Telegram', 'ID_Card', 'Username', 'Saldo', 'Nome_Auletta', 'Verificato?', 'Admin?']
    rows = GetUsersExcel()

    rowsDataframe = []

    for id_t, id_c, u, s, n, v, a in rows:
        tempArr = []
        tempArr.append(id_t)
        tempArr.append(id_c)
        tempArr.append(u)
        tempArr.append(s)
        tempArr.append(n)
        tempArr.append(v)
        tempArr.append(a)
        rowsDataframe.append(tempArr)

    df = pandas.DataFrame(rowsDataframe, columns=columns)

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)  # Riposiziona il cursore all'inizio del buffer

    await context.bot.send_document(chat_id=f"{GetChannelID()}", document=excel_buffer, filename=f'ResocontoUtenti-{datetime.date(datetime.now())}.xlsx', caption=f"Resoconto utenti del {datetime.date(datetime.now())} inviato!")