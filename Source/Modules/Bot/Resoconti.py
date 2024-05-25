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
        date = datetime(do.year, do.month, do.day, do.hour, do.minute, do.second, do.microsecond)
        tempArr = [id_o, id_t, u, na, pr, c, pa, date]        
        rowsOperazioniDataframe.append(tempArr)

    for id_r, id_b, u_b, id_a, u_a, i, sp, sd, dt_r in rowsRicariche:
        date = datetime(dt_r.year, dt_r.month, dt_r.day, dt_r.hour, dt_r.minute, dt_r.second, dt_r.microsecond)
        tempArr = [id_r, id_b, u_b, id_a, u_a, i, sp, sd, date]
        rowsRicaricheDataframe.append(tempArr)

    # Creazione del DataFrame
    dfOperazioni = pandas.DataFrame(rowsOperazioniDataframe, columns=columnsOperazioni)
    dfRicariche = pandas.DataFrame(rowsRicaricheDataframe, columns=columnsRicariche)

    excel_buffer = BytesIO()
    
    with pandas.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        dfOperazioni.to_excel(writer, sheet_name='Operazioni', index=False)
        dfRicariche.to_excel(writer, sheet_name='Ricariche', index=False)

        worksheet_operazioni = writer.sheets['Operazioni']
        worksheet_ricariche = writer.sheets['Ricariche']

        # Imposta la larghezza delle colonne per 'Operazioni'
        for i, col in enumerate(dfOperazioni.columns):
            max_len = max(
                dfOperazioni[col].astype(str).map(len).max(),  # lunghezza massima dei dati
                len(col)  # lunghezza del nome della colonna
            ) + 2  # margine extra
            worksheet_operazioni.set_column(i, i, max_len)
        
        # Imposta la larghezza delle colonne per 'Ricariche'
        for i, col in enumerate(dfRicariche.columns):
            max_len = max(
                dfRicariche[col].astype(str).map(len).max(),  # lunghezza massima dei dati
                len(col)  # lunghezza del nome della colonna
            ) + 2  # margine extra
            worksheet_ricariche.set_column(i, i, max_len)

    excel_buffer.seek(0)  # Riposiziona il cursore all'inizio del buffer

    await context.bot.send_document(chat_id=f"{GetChannelID()}", document=excel_buffer, filename=f'Resoconto-{datetime.date(datetime.now())}.xlsx', caption=f"Resoconto del {datetime.date(datetime.now())} inviato!")
    excel_buffer.close()


async def SendUsersResoconto(context: CallbackContext):
    
    columns = ['ID_Telegram', 'ID_Card', 'Username', 'Saldo', 'Nome_Auletta', 'Verificato?', 'Admin?']
    rows = GetUsersExcel()

    rowsDataframe = []

    for id_t, id_c, u, s, n, v, a in rows:
        tempArr = [id_t, id_c, u, s, n, v, a]
        rowsDataframe.append(tempArr)

    df = pandas.DataFrame(rowsDataframe, columns=columns)

    excel_buffer = BytesIO()
    
    with pandas.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Utenti')
        
        worksheet = writer.sheets['Utenti']
        
        # Imposta la larghezza delle colonne
        for i, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).map(len).max(),  # lunghezza massima dei dati
                len(col)  # lunghezza del nome della colonna
            ) + 2  # margine extra
            worksheet.set_column(i, i, max_len)
    
    
    excel_buffer.seek(0)  # Riposiziona il cursore all'inizio del buffer

    await context.bot.send_document(chat_id=f"{GetChannelID()}", document=excel_buffer, filename=f'ResocontoUtenti-{datetime.date(datetime.now())}.xlsx', caption=f"Resoconto utenti del {datetime.date(datetime.now())} inviato!")
    excel_buffer.close()