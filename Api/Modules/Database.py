from mysql.connector import cursor, connect, MySQLConnection
from Modules.Configs import GetDBHost, GetDBUsername, GetDBPassword, GetDBDatabase

import datetime

def TryConnect() -> MySQLConnection:    
    """DATABASE_HANDLER: Prova a connettersi al DB tramite i parametri, altrimenti da errore"""

    try:
        cnx : MySQLConnection = connect(
            host=GetDBHost(),
            user=GetDBUsername(),
            password=GetDBPassword(),
            database=GetDBDatabase()
        )

        return cnx

    except Exception as e:  
        print("Non è stato possibile connettersi al DB.")
        print(e)
        exit(-1)

def TryDisconnect(cnx : MySQLConnection, crs : cursor.MySQLCursor) -> None:
    """DATABASE_HANDLER: Prova a disconnetersi dalla connessione e dal cursore passati come parametro"""
    
    try:
        crs.close()
        cnx.close()
    except Exception as e:
        ("Non è stato possibile chiudere la connessione. ABORT.")
        print(e)
        exit(-1)

def GetAulette() -> list:
    """DATABASE_HANDLER / ADD_USER: Prendiamo tutti gli id ed i nomi delle aulette"""

    query = "SELECT ID_Auletta, Nome FROM Auletta;"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()
    
    crs.execute(query)

    rows = crs.fetchall()

    TryDisconnect(cnx=cnx, crs=crs)

    return rows

def GetBalance(idTelegram : str) -> float:
    """DATABASE_HANDLER / SHOW_BALANCE: Prende il saldo dell'utente con ID_Telegram passato come parametro"""
    
    print(f"IDTELEGRAM: {idTelegram}")

    query = f"SELECT Saldo FROM Utente WHERE ID_Telegram = '{idTelegram}';"
    
    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    saldo = crs.fetchone()[0]

    TryDisconnect(cnx=cnx, crs=crs)

    return float(saldo)

def GetIDTelegram(idCard : int) -> str:
    
    query = f"SELECT ID_Telegram FROM Utente WHERE ID_Card = '{idCard}';"
    
    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    idTelegram = crs.fetchone()[0]

    TryDisconnect(cnx=cnx, crs=crs)

    return idTelegram

def QuantitaECosto(ID_Prodotto : int, ID_Auletta : int) -> list:
    """ Controllare quanto costa un elemento in una determinata auletta e controllare se esiste almeno un unità in vendita """
    queryCosto = f"SELECT Quantità, Costo FROM Magazzino WHERE ID_Prodotto = '{ID_Prodotto}' AND ID_Auletta = '{ID_Auletta}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(queryCosto)

    row = crs.fetchone()

    TryDisconnect(cnx=cnx, crs=crs)
    
    return row

def GetDebito(ID_Auletta : int) -> int:
    query = f"SELECT DebitoMax FROM Auletta WHERE ID_Auletta = '{ID_Auletta}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)

    debito = crs.fetchone()[0]
    
    TryDisconnect(cnx=cnx, crs=crs)

    return debito

def CreateOperazione(ID_Telegram : str, ID_Auletta : int, ID_Prodotto : int, costo : int) -> None:
    now : datetime.datetime = datetime.datetime.now()
    
    query = f"INSERT INTO Operazione (ID_Telegram, ID_Auletta, ID_Prodotto, DateTimeStamp, Costo) VALUES ('{ID_Telegram}', '{ID_Auletta}', '{ID_Prodotto}', '{now}', '{costo}');"
    
    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    cnx.commit()

    TryDisconnect(cnx=cnx, crs=crs)

def DecurtaSaldo(ID_Telegram : str, saldo : float) -> None:
    query = f"UPDATE Utente SET Saldo = '{saldo}' WHERE ID_Telegram = '{ID_Telegram}';"
    
    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    cnx.commit()

    TryDisconnect(cnx=cnx, crs=crs)

def DecurtaMagazzino(idProdotto : int, idAuletta : int, quantita : int):
    query = f"UPDATE Magazzino SET Quantità = '{quantita}' WHERE ID_Prodotto = '{idProdotto}' AND ID_Auletta = '{idAuletta}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    cnx.commit()

    TryDisconnect(cnx=cnx, crs=crs)

# TODO: Sistemare notazione
def PayDB(ID_Prodotto : int, ID_Auletta : int, ID_Card : int) -> list:
    """DATABASE_HANDLER / WEMOS: In base all'auletta ed all'utente, far pagare il giusto"""

    quancosto : list = QuantitaECosto(ID_Prodotto=ID_Prodotto, ID_Auletta=ID_Auletta)
    quantita : int = quancosto[0]
    costo : float = quancosto[1]

    idTelegram : str = GetIDTelegram(idCard=ID_Card)

    saldo : float = GetBalance(idTelegram=idTelegram)

    debito : float = float(GetDebito(ID_Auletta=ID_Auletta))

    # Controllare se quantità disponibile

    if quantita <= 0:
        return {"Error" : "Quantità dell'item inferiore a 0"}
    
    # Calcola il totale del debito possibile
    debitoMassimo = debito * costo

    # Calcola il totale disponibile (saldo + debito massimo)
    totaleDisponibile = saldo + debitoMassimo

    # Verifica se l'utente può permettersi il prodotto
    if totaleDisponibile < costo:
        return { "Error" : "Saldo Insufficiente" }

    # Decurtatre saldo
    saldo -= costo
    DecurtaSaldo(ID_Telegram=idTelegram, saldo=saldo)

    # Scalare dal magazzino un unità di quel tipo
    quantita -= 1
    DecurtaMagazzino(idProdotto=ID_Prodotto, idAuletta=ID_Auletta, quantita=quantita)

    # Creare storico della transazione come "Eseguito"
    CreateOperazione(ID_Telegram=idTelegram, ID_Auletta=ID_Auletta, ID_Prodotto= ID_Prodotto, costo=costo)

    return {"State" : "Comprato"}
