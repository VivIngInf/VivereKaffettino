# Librerie DB
from mysql.connector import cursor, connect, MySQLConnection
from TelegramBot.LoadConfig import GetHost, GetUsername, GetPassword, GetDatabase

# TODO: Inserire l'utente nel db

def TryConnect() -> MySQLConnection:    
    """DATABASE_HANDLER: Prova a connettersi al DB tramite i parametri, altrimenti da errore"""

    try:
        cnx : MySQLConnection = connect(
            host=GetHost(),
            user=GetUsername(),
            password=GetPassword(),
            database=GetDatabase()
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
        ("Non è s tato possibile chiudere la connessione. ABORT.")
        print(e)
        exit(-1)

def GetAulette():
    """DATABASE_HANDLER / INSERT_USER: Prendiamo tutti gli id ed i nomi delle aulette"""

    query = "SELECT ID_Auletta, Nome FROM Auletta;"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()
    
    crs.execute(query)

    rows = crs.fetchall()

    TryDisconnect(cnx=cnx, crs=crs)

    return rows

def GetBalance(idTelegram : str) -> float:
    """SHOW_BALANCE: Prende il saldo dell'utente con ID_Telegram passato come parametro"""
    
    query = f"SELECT Saldo FROM Utente WHERE ID_Telegram = '{idTelegram}';"
    
    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    saldo = crs.fetchone()[0]

    TryDisconnect(cnx=cnx, crs=crs)

    return float(saldo)