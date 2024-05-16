from telegram.ext import  CallbackContext
from ..Shared.Configs import GetChannelID
from ..Shared.Query import GetOperazioniExcel, GetUsersExcel, GetRicaricheExcel
import pandas
from io import BytesIO
from datetime import datetime

async def SendDailyResoconto(context: CallbackContext):
    columnsOperazioni = ['ID_Operazione', 'ID_Telegram', 'Username', 'Nome_Auletta', 'Prodotto', 'Costo', 'Pagato', 'Data_Ora']
    columnsRicariche = ['ID_Ricarica', 'ID_Beneficiario', 'Username_Beneficiario', 'ID_Amministratore', 'Username_Amministratore', 'Importo', 'Saldo_Prima', 'Saldo_Dopo', 'Date_Time_Ricarica']

    rowsOperazioni = GetOperazioniExcel()
    rowsRicariche = GetRicaricheExcel()
    print(rowsRicariche)

    rowsOperazioniDataframe = []
    rowsRicaricheDataframe = []

    for id_o, id_t, u, na, pr, c, pa, do in rowsOperazioni:
        tempArr = []
        tempArr.append(id_o)
        tempArr.append(id_t)
        tempArr.append(u)
        tempArr.append(na)
        tempArr.append(pr)
        tempArr.append(c)
        tempArr.append(pa)
        tempArr.append(datetime(do.year, do.month, do.day, do.hour, do.minute, do.second, do.microsecond))
        rowsOperazioniDataframe.append(tempArr)

    for id_r, id_b, u_b, id_a, u_a, i, sp, sd, dt_r in rowsRicariche:
        tempArr = []
        tempArr.append(id_r)
        tempArr.append(id_b)
        tempArr.append(u_b)
        tempArr.append(id_a)
        tempArr.append(u_a)
        tempArr.append(i)
        tempArr.append(sp)
        tempArr.append(sd)
        tempArr.append(datetime(dt_r.year, dt_r.month, dt_r.day, dt_r.hour, dt_r.minute, dt_r.second, dt_r.microsecond))
        rowsRicaricheDataframe.append(tempArr)

    # Creazione del DataFrame
    dfOperazioni = pandas.DataFrame(rowsOperazioniDataframe, columns=columnsOperazioni)
    dfRicariche = pandas.DataFrame(rowsRicaricheDataframe, columns=columnsRicariche)

    excel_buffer = BytesIO()
    
    with pandas.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        dfOperazioni.to_excel(writer, sheet_name='Operazioni', index=False)
        dfRicariche.to_excel(writer, sheet_name='Ricariche', index=False)

    excel_buffer.seek(0)  # Riposiziona il cursore all'inizio del buffer

    await context.bot.send_document(chat_id=f"{GetChannelID()}", document=excel_buffer, filename=f'Resoconto-{datetime.date(datetime.now())}.xlsx', caption=f"Resoconto del {datetime.date(datetime.now())} inviato!")
    excel_buffer.close()


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