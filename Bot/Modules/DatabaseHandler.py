# Librerie DB
from mysql.connector import cursor, connect, MySQLConnection
from Modules.LoadConfig import GetDBHost, GetDBUsername, GetDBPassword, GetDBDatabase

# TODO: Notificare dell'inserimento dell'utente il gruppo degli amministratori dell'auletta selezionata

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

def CheckUserExists(idTelegram : str) -> bool:
    """DATABASE_HANDLER / ADD_USER: Controlla se l'utente esiste dato un ID_Telegram, ritorna un valore booleano"""

    query = f"SELECT EXISTS (SELECT 1 FROM Utente WHERE ID_Telegram = '{idTelegram}');"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)

    userExists = crs.fetchone()[0]

    return bool(userExists)

def GetUsername(idTelegram : str) -> str:
    """DATABASE_HANDLER / USER_INFO: Ritorna l'username partendo dall'ID_Telegram passato come parametro"""

    query = f"SELECT Username FROM Utente WHERE ID_Telegram = '{idTelegram}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)

    username : str = crs.fetchone()[0]

    crs.close()
    cnx.close()

    return username

def GetIdTelegram(username : str) -> str:
    """DATABASE_HANDLER: Ritorna l'ID_Telegram partendo dall'Username passato come parametro"""

    query = f"SELECT ID_Telegram FROM Utente WHERE Username = '{username}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)

    idTelegram : str = crs.fetchone()[0]

    crs.close()
    cnx.close()

    return idTelegram

def GetAulette() -> list:
    """DATABASE_HANDLER / ADD_USER: Prendiamo tutti gli id ed i nomi delle aulette"""

    query = "SELECT ID_Auletta, Nome FROM Auletta;"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()
    
    crs.execute(query)

    rows = crs.fetchall()

    TryDisconnect(cnx=cnx, crs=crs)

    return rows

def GetAuletta(idAuletta : int) -> str:
    """DATABASE_HANDLER / ADD_USER: Dato l'ID di un'auletta, restituisce il suo nome"""

    query = f"SELECT Nome From Auletta WHERE ID_Auletta = '{idAuletta}';"

    cnx = TryConnect()
    crs = cnx.cursor()

    crs.execute(query)
    nomeAuletta = crs.fetchone()[0]

    crs.close()
    cnx.close()

    return str(nomeAuletta)

def InsertUser(idTelegram : str, username : str) -> None: 
    """DATABASE_HANDLER / ADD_USER: Inserisce l'utente con ID_Telegram ed Username passati come parametro nel DB"""

    query = f"INSERT INTO Utente (ID_Telegram, Username) VALUES ('{idTelegram}', '{username}');"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    cnx.commit() 

    TryDisconnect(cnx=cnx, crs=crs)

    return None

def GetBalance(idTelegram : str) -> float:
    """DATABASE_HANDLER / SHOW_BALANCE: Prende il saldo dell'utente con ID_Telegram passato come parametro"""
    
    query = f"SELECT Saldo FROM Utente WHERE ID_Telegram = '{idTelegram}';"
    
    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    saldo = crs.fetchone()[0]

    TryDisconnect(cnx=cnx, crs=crs)

    return float(saldo)

def SetAdminDB(idTelegram : str, state : bool) -> None:
    """DATABASE_HANDLER / ADD_ADMIN: Aggiorniamo l'utente con idTelegram passato come parametro impostando
    isAdmin ad 1"""

    query = f"UPDATE Utente SET IsAdmin = {int(state)} WHERE ID_Telegram = '{idTelegram}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    cnx.commit()

    TryDisconnect(cnx, crs)

    return None

def GetIsAdmin(idTelegram : str) -> bool:
    """DATABASE_HANDLER: Ritorna il ruolo dell'utente"""
    
    query = f"SELECT IsAdmin FROM Utente WHERE ID_Telegram = '{idTelegram}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    isAdmin = crs.fetchone()[0]

    TryDisconnect(cnx=cnx, crs=crs)

    return bool(isAdmin)

def GetIsVerified(idTelegram : str) -> bool:
    """DATABASE_HANDLER: Ritorna se l'utente è stato approvato"""
    
    query = f"SELECT IsVerified From Utente WHERE ID_TELEGRAM = '{idTelegram}'"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    isVerified = crs.fetchone()[0]

    TryDisconnect(cnx=cnx, crs=crs)

    return bool(isVerified)