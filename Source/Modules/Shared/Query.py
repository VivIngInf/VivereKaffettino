from mysql.connector import cursor, connect, MySQLConnection
from .Configs import GetDBHost, GetDBUsername, GetDBPassword, GetDBDatabase

from ...persisting import session
from sqlalchemy import select

from ..Database.Models.Auletta import Auletta
from ..Database.Models.Magazzino import Magazzino
from ..Database.Models.Operazione import Operazione
from ..Database.Models.Prodotto import Prodotto
from ..Database.Models.Ricarica import Ricarica
from ..Database.Models.Rifornimento import Rifornimento
from ..Database.Models.Utente import Utente

import datetime

# TODO: Notificare dell'inserimento dell'utente il gruppo degli amministratori dell'auletta selezionata

#region Connection

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

#endregion

#region User

def CheckUserExists(idTelegram : str) -> bool:
    """DATABASE_HANDLER / ADD_USER: Controlla se l'utente esiste dato un ID_Telegram, ritorna un valore booleano"""

    query = f"SELECT EXISTS (SELECT 1 FROM Utente WHERE ID_Telegram = '{idTelegram}');"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)

    userExists = crs.fetchone()[0]

    return bool(userExists)

def CheckUsernameExists(username : str) -> bool:
    """DATABASE_HANDLER: Controlla se l'username è già stato preso"""

    query = f"SELECT EXISTS (SELECT 1 FROM Utente WHERE Username = '{username}');"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)

    usernameExists = crs.fetchone()[0]

    return bool(usernameExists)

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

def GetIDTelegram(idCard : int) -> str:
    
    query = f"SELECT ID_Telegram FROM Utente WHERE ID_Card = '{idCard}';"
    
    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    idTelegram : str = crs.fetchone()[0]

    TryDisconnect(cnx=cnx, crs=crs)

    return idTelegram

def InsertUser(idTelegram : str, username : str) -> None: 
    """DATABASE_HANDLER / ADD_USER: Inserisce l'utente con ID_Telegram ed Username passati come parametro nel DB"""

    query = f"INSERT INTO Utente (ID_Telegram, Username) VALUES ('{idTelegram}', '{username}');"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    cnx.commit() 

    TryDisconnect(cnx=cnx, crs=crs)

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

def DecurtaSaldo(ID_Telegram : str, saldo : float) -> None:
    query = f"UPDATE Utente SET Saldo = '{saldo}' WHERE ID_Telegram = '{ID_Telegram}';"
    
    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    cnx.commit()

    TryDisconnect(cnx=cnx, crs=crs)

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

#endregion

#region Aulette

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

#endregion

#region Admin
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
#endregion

#region Magazzino

def QuantitaECosto(ID_Prodotto : int, ID_Auletta : int) -> list:
    """ Controllare quanto costa un elemento in una determinata auletta e controllare se esiste almeno un unità in vendita """
    queryCosto = f"SELECT Quantità, Costo FROM Magazzino WHERE ID_Prodotto = '{ID_Prodotto}' AND ID_Auletta = '{ID_Auletta}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(queryCosto)

    row = crs.fetchone()

    TryDisconnect(cnx=cnx, crs=crs)
    
    return row

def DecurtaMagazzino(idProdotto : int, idAuletta : int, quantita : int):
    query = f"UPDATE Magazzino SET Quantità = '{quantita}' WHERE ID_Prodotto = '{idProdotto}' AND ID_Auletta = '{idAuletta}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    cnx.commit()

    TryDisconnect(cnx=cnx, crs=crs)

#endregion

#region Auletta

def GetDebito(ID_Auletta : int) -> int:
    query = f"SELECT DebitoMax FROM Auletta WHERE ID_Auletta = '{ID_Auletta}';"

    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)

    debito = crs.fetchone()[0]
    
    TryDisconnect(cnx=cnx, crs=crs)

    return debito

#endregion

#region Operazione

def CreateOperazione(ID_Telegram : str, ID_Auletta : int, ID_Prodotto : int, costo : int) -> None:
    now : datetime.datetime = datetime.datetime.now()
    
    query = f"INSERT INTO Operazione (ID_Telegram, ID_Auletta, ID_Prodotto, DateTimeStamp, Costo) VALUES ('{ID_Telegram}', '{ID_Auletta}', '{ID_Prodotto}', '{now}', '{costo}');"
    
    cnx : MySQLConnection = TryConnect()
    crs : cursor.MySQLCursor = cnx.cursor()

    crs.execute(query)
    cnx.commit()

    TryDisconnect(cnx=cnx, crs=crs)

#endregion

#region Wemos

# TODO: Sistemare notazione
def PayDB(ID_Prodotto : int, ID_Auletta : int, ID_Card : int) -> list:
    
    query = select(Utente)
    result = session.scalar(query)

    return result

    """DATABASE_HANDLER / WEMOS: In base all'auletta ed all'utente, far pagare il giusto"""

"""    quancosto : list = QuantitaECosto(ID_Prodotto=ID_Prodotto, ID_Auletta=ID_Auletta)
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

    return {"State" : "Comprato"}"""

    

#endregion