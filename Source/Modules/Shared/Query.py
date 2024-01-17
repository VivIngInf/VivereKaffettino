from mysql.connector import cursor, connect, MySQLConnection
from .Configs import GetDBHost, GetDBUsername, GetDBPassword, GetDBDatabase

from .Session import session
from sqlalchemy import select, func
from sqlalchemy.orm import aliased

from ..Database.Models.Auletta import Auletta
from ..Database.Models.Magazzino import Magazzino
from ..Database.Models.Operazione import Operazione
from ..Database.Models.Prodotto import Prodotto
from ..Database.Models.Ricarica import Ricarica
from ..Database.Models.Rifornimento import Rifornimento
from ..Database.Models.Utente import Utente

import datetime

# TODO: Notificare dell'inserimento dell'utente il gruppo degli amministratori dell'auletta selezionata
# TODO: Quando si effettua un pagamento, controllare la validità dei parametri passati (ES: Esiste l'auletta? Esiste un utente con quell'ID_Card?)

#region User

def CheckUserExists(idTelegram : str) -> bool:
    """DATABASE_HANDLER / ADD_USER: Controlla se l'utente esiste dato un ID_Telegram, ritorna un valore booleano"""

    query = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}")
    exists = session.query(query.exists()).scalar()

    return bool(exists)

def CheckUsernameExists(username : str) -> bool:
    """DATABASE_HANDLER: Controlla se l'username è già stato preso"""

    exists = session.query(Utente).filter(Utente.username == f"{username}").exists()

    return bool(exists)

def GetUsername(idTelegram : str) -> str:
    """DATABASE_HANDLER / USER_INFO: Ritorna l'username partendo dall'ID_Telegram passato come parametro"""
    return session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().username

def GetIdTelegram(username : str) -> str:
    """DATABASE_HANDLER: Ritorna l'ID_Telegram partendo dall'Username passato come parametro"""

    return session.query(Utente).filter(Utente.username == f"{username}").one().ID_Telegram

def GetIDTelegram(idCard : str) -> str:
    """DATABASE_HANDLER: Ritorna l'ID_Telegram partendo dall'ID della carta passato come parametro"""

    return session.query(Utente).filter(Utente.ID_Card == f"{idCard}").one().ID_Telegram

def InsertUser(idTelegram : str, username : str) -> None: 
    """DATABASE_HANDLER / ADD_USER: Inserisce l'utente con ID_Telegram ed Username passati come parametro nel DB"""

    utente = Utente(
        ID_Telegram=idTelegram,
        username=username,
        ID_Card=None,
        saldo=0.0,
        isAdmin=False,
        isVerified=False,
    )

    session.add(utente)
    session.commit()

    return None

def GetIsAdmin(idTelegram : str) -> bool:
    """DATABASE_HANDLER: Ritorna il ruolo dell'utente"""

    return bool(session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().isAdmin)

def GetIsVerified(idTelegram : str) -> bool:
    """DATABASE_HANDLER: Ritorna se l'utente è stato approvato"""
    user : Utente = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").scalar()
    return bool(user.isVerified)

def DecurtaSaldo(ID_Telegram : str, saldo : float) -> None:    
    
    user = session.query(Utente).filter(Utente.ID_Telegram == f"{ID_Telegram}").one()
    
    user.saldo = round(saldo, 2)

    session.commit()

def GetBalance(idTelegram : str) -> float:
    """DATABASE_HANDLER / SHOW_BALANCE: Prende il saldo dell'utente con ID_Telegram passato come parametro"""
    return session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().saldo

def getStoricoPersonale(idTelegram : str) -> list:
    """
        USER: Ritorna tuto lo storico personale
    """
    return session.query(Operazione).filter(Operazione.ID_Telegram == f"{idTelegram}").all()

#endregion

#region Aulette

def GetAulette() -> list:
    """DATABASE_HANDLER / ADD_USER: Prendiamo tutti gli id ed i nomi delle aulette"""

    return session.query(Auletta).all()

def GetAuletta(idAuletta : int) -> str:
    """DATABASE_HANDLER / ADD_USER: Dato l'ID di un'auletta, restituisce il suo nome"""

    return session.query(Auletta).filter(Auletta.ID_Auletta == f"{idAuletta}").one().Nome

#endregion

#region Admin
def SetAdminDB(idTelegram : str, state : bool) -> None:
    """DATABASE_HANDLER / ADD_ADMIN: Aggiorniamo l'utente con idTelegram passato come parametro impostando
    isAdmin"""

    u : Utente = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one()
    u.isAdmin = state

    session.commit()

    return None

def getCaffeGiornalieri() -> int:
    """ADMIN: Ritorna il numero dei caffé fatti in questo giorno"""
    return session.query(Operazione).filter(func.date(Operazione.dateTimeOperazione) == datetime.date.today(), Operazione.ID_Prodotto == 1).count()

def getOperazioniGiornaliere() -> list:
    """ADMIN: Ritorna tutte le operazioni giornaliere"""
    return session.query(Operazione).filter(func.date(Operazione.dateTimeOperazione) == datetime.date.today()).all()

def incrementaSaldo(username : str, ricarica : float) -> int:
    """
        ADMIN: Incrementa il saldo in base alla ricarica passata come parametro
        
        Parameters:
            - username: l'username dell'utente alla quale aumentare il saldo
            - ricarica: di quanto incrementare il saldo dell'utente

        Returns:
            - 0 se l'utente non esiste
            - 1 se il saldo è stato incrementato correttamente
    """
    
    if not CheckUserExists():
        return 0

    ID_Telegram = GetIdTelegram(username=username)

    user = session.query(Utente).filter(Utente.ID_Telegram == f"{ID_Telegram}").one()
    
    user.saldo = round(user.saldo + ricarica, 2)

    session.commit()

    return 1

def getUsers() -> list:
    """
        ADMIN: Ritorna tutti gli utenti
    """
    return session.query(Utente).all()

def removeUser(idTelegram : str) -> dict:
    """
        ADMIN: Rimuove l'utente con ID_Telegram idTelegram
    """
    if not CheckUserExists(idTelegram=idTelegram):
        return {"Error" : "Utente non esistente"}
    
    session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").delete()
    session.commit()

    return {"State" : "Utente con ID_Telegram: '{idTelegram}' cancellato!"}

#endregion

#region Magazzino

def QuantitaECosto(ID_Prodotto : int, ID_Auletta : int) -> Magazzino:
    """ Controllare quanto costa un elemento in una determinata auletta e controllare se esiste almeno un unità in vendita """

    result = session.query(Magazzino).filter(Magazzino.ID_Prodotto == f"{ID_Prodotto}", Magazzino.ID_Auletta == f"{ID_Auletta}").one()

    return result

def DecurtaMagazzino(idProdotto : int, idAuletta : int, quantita : int) -> dict:

    magazzino = session.query(Magazzino).filter(Magazzino.ID_Prodotto == f"{idProdotto}", Magazzino.ID_Auletta == f"{idAuletta}").one()
    
    magazzino.quantita -= quantita

    session.commit()

    return {"State" : "Done"}

def GetProdotti(idAuletta : int) -> str:
    """WEB_API: Dato l'ID di un'auletta, restituisce i suoi prodotti"""

    arr = []

    class Prodotti:
        ID_Prodotto : int
        descrizione : str
        costo : float

    res = session.query(Prodotto.ID_Prodotto, Prodotto.descrizione, Magazzino.costo).join(Prodotto, Prodotto.ID_Prodotto == Magazzino.ID_Prodotto).filter(Magazzino.ID_Auletta == idAuletta).all()
    
    for r in res:        
        p = Prodotti()
        
        p.ID_Prodotto = r[0]
        p.descrizione = r[1]
        p.costo = r[2]

        arr.append(p)

    return arr

def getMagazzino(idAuletta : int) -> list:
    """
        MAGAZZINO: Ritorna tutti i prodotti e la quantità in magazzino dell'auletta con id idAuletta
    """
    return session.query(Magazzino).filter(Magazzino.ID_Auletta == f"{idAuletta}").all()

def ricaricaMagazzino(idAuletta : str, idProdotto : int, quantitaRicaricata : int) -> int:
    """
        MAGAZZINO: Ricarica di una quantità pari a quantitaRicaricata il prodotto con id idProdotto nell'auletta con id idAuletta.
        RITORNA:
            - 0 se tutto andato a buon fine
            - 1 se auletta non esiste
            - 2 se idProdotto non esiste
            - 3 se quantità ricaricata è <= 0
    """
    # TODO: Implementare auletta non esistente e prodotto non esistente

    if quantitaRicaricata <= 0:
        return {"Error" : "Quantità ricaricata non positiva"}
    
    magazzino = session.query(Magazzino).filter(Magazzino.ID_Auletta == f"{idAuletta}", Magazzino.ID_Prodotto == f"{idProdotto}").one()
    
    magazzino.quantita = round(magazzino.quantita + quantitaRicaricata, 2)

    session.commit()

    return {"State" : "Done"}

#endregion

#region Auletta

def GetDebito(ID_Auletta : int) -> int:
    return session.query(Auletta).filter(Auletta.ID_Auletta == f"{ID_Auletta}").one().DebitoMax

#endregion

#region Operazione

def CreateOperazione(ID_Telegram : str, ID_Auletta : int, ID_Prodotto : int, costo : int) -> None:
    now : datetime.datetime = datetime.datetime.now()
    
    operazione = Operazione(
        ID_Operazione=None,
        ID_Telegram= ID_Telegram,
        ID_Auletta=ID_Auletta,
        ID_Prodotto=ID_Prodotto,
        dateTimeOperazione=now,
        costo=costo
    )

    session.add(operazione)
    session.commit()    


#endregion

#region Wemos

# TODO: Sistemare notazione
def PayDB(ID_Prodotto : int, ID_Auletta : int, ID_Card : str) -> int:
    
    """users = session.query(Utente).all()

    return statecode"""

    """DATABASE_HANDLER / WEMOS: In base all'auletta ed all'utente, far pagare il giusto"""

    try:

        magazzino : Magazzino = QuantitaECosto(ID_Prodotto=ID_Prodotto, ID_Auletta=ID_Auletta)
        costo = magazzino.costo

    except:
        return 3 # Prodotto con ID {ID_Prodotto} non è stato trovato nell'auletta con ID {ID_Auletta}. Oppure uno dei due non esiste completamente.

    try:
        idTelegram : str = GetIDTelegram(idCard=ID_Card)
    except:
        return 2 # Utente con idCard {ID_Card} non esistente


    saldo : float = GetBalance(idTelegram=idTelegram)

    debito : float = GetDebito(ID_Auletta=ID_Auletta)

    # Controllare se quantità disponibile

    if magazzino.quantita <= 0:
        return 4 # Quantità dell'item inferiore a 0
    
    # Calcola il totale del debito possibile
    debitoMassimo = debito * costo

    # Calcola il totale disponibile (saldo + debito massimo)
    totaleDisponibile = saldo + debitoMassimo

    # Verifica se l'utente può permettersi il prodotto
    if totaleDisponibile < costo:
        return 1 # Saldo non sufficiente

    # Decurtatre saldo
    saldo -= costo
    DecurtaSaldo(ID_Telegram=idTelegram, saldo=saldo)

    # Scalare dal magazzino un unità di quel tipo
    DecurtaMagazzino(idProdotto=ID_Prodotto, idAuletta=ID_Auletta, quantita=1)

    try:
        # Creare storico della transazione come "Eseguito"
        CreateOperazione(ID_Telegram=idTelegram, ID_Auletta=ID_Auletta, ID_Prodotto=ID_Prodotto, costo=costo)
    except:
        return 5 # Non è stato possibile creare lo storico dell'operazione avvenuta TODO: Restituire soldi e non far partire il caffè

    return 0 # Comprato

#endregion