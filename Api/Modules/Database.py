from mysql.connector import cursor, connect, MySQLConnection
from Modules.Configs import GetDBHost, GetDBUsername, GetDBPassword, GetDBDatabase

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

    debito = crs.fetchone()
    
    TryDisconnect(cnx=cnx, crs=crs)

    return debito

def PayDB(ID_Prodotto : int, ID_Auletta : int, ID_Card : int) -> list:
    """DATABASE_HANDLER / WEMOS: In base all'auletta ed all'utente, far pagare il giusto"""

    quancosto = QuantitaECosto(ID_Prodotto=ID_Prodotto, ID_Auletta=ID_Auletta)
    quantita = quancosto[0]
    costo = quancosto[1]

    idTelegram = GetIDTelegram(idCard=ID_Card)

    saldo = GetBalance(idTelegram=idTelegram)

    debito = GetDebito(ID_Auletta=ID_Auletta)

    # Controllare se quantità disponibile

    if quantita <= 0:
        return {"Error" : "Quantità dell'item inferiore a 0"}
    
    # Controllare se si ha abbastanza soldi per non andare fuori debito max
    
    saldo -= costo
    debito = costo * debito    

    if saldo >= 0:
        return{"Status" : "Approved"}

    if saldo <= debito:
        return{"Status" : f"Indebitato di {saldo}€"}

    # TODO: Creare storico della transazione come "Non eseguita"
    # TODO: Decurtatre saldo
    # TODO: Scalare dal magazzino un unità di quel tipo
    # TODO: Modificare storico della transazione come "Eseguito"