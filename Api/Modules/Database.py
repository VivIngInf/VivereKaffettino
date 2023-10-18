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

def PayDB(ID_Prodotto : int, ID_Auletta : int) -> list:
    """DATABASE_HANDLER / WEMOS: In base all'auletta ed all'utente, far pagare il giusto"""
    queryCosto = f"SELECT Quantità, Costo FROM Magazzino WHERE ID_Prodotto == {ID_Prodotto} AND WHERE ID_Auletta == {ID_Auletta}"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(queryCosto)

    row = crs.fetchone()
    quantita = row[0]
    costo = row[1]

    return row

    # TODO: Controllare quanto costa un elemento in una determinata auletta
    # TODO: Controllare se si ha abbastanza soldi per non andare fuori debito max
    # TODO: Creare storico della transazione come "Non eseguita"
    # TODO: Decurtatre saldo
    # TODO: Scalare dal magazzino un unità di quel tipo
    # TODO: Modificare storico della transazione come "Eseguito"