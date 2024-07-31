from mysql.connector import cursor, connect, MySQLConnection

from .Session import session
from sqlalchemy import select, func, distinct
from sqlalchemy.orm import aliased, load_only

from ..Database.Models.Auletta import Auletta
from ..Database.Models.Magazzino import Magazzino
from ..Database.Models.Operazione import Operazione
from ..Database.Models.Prodotto import Prodotto
from ..Database.Models.Ricarica import Ricarica
from ..Database.Models.Rifornimento import Rifornimento
from ..Database.Models.Utente import Utente
from ..Bot.BirthdayList import compleanniRiscattati

import datetime
from os import environ

# TODO: Notificare dell'inserimento dell'utente il gruppo degli amministratori dell'auletta selezionata
# TODO: Quando si effettua un pagamento, controllare la validità dei parametri passati (ES: Esiste l'auletta? Esiste un utente con quell'ID_Card?)
# TODO: Quando si effettua la decurtazione dell'importo, prima controllare se è il compleanno del ragazzo.
# TODO: Quando si effettua il login, controllare se è il compleanno e mandare una foto adeguata.
# TODO: Implementare CheckCardExists anche per l'utente base e per il cambio di carta

# region User

def CheckUserExists(idTelegram: str) -> bool:
    """DATABASE_HANDLER / ADD_USER: Controlla se l'utente esiste dato un ID_Telegram, ritorna un valore booleano"""

    query = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}")
    exists = session.query(query.exists()).scalar()

    return bool(exists)


def CheckUsernameExists(username: str) -> str:
    """DATABASE_HANDLER: Controlla se l'username è già stato preso"""

    exists = (session.query(Utente).filter(Utente.username == f"{username}").exists()).scalar()

    return bool(exists)


def GetUsername(idTelegram: str) -> str:
    """DATABASE_HANDLER / USER_INFO: Ritorna l'username partendo dall'ID_Telegram passato come parametro"""
    return session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().username


def GetIdTelegram(username: str) -> str:
    """DATABASE_HANDLER: Ritorna l'ID_Telegram partendo dall'Username passato come parametro"""
    try:
        return session.query(Utente).filter(Utente.username == f"{username}").one().ID_Telegram
    except:
        return "None"


def GetIDTelegram(idCard: str) -> str:
    """DATABASE_HANDLER: Ritorna l'ID_Telegram partendo dall'ID della carta passato come parametro"""

    return session.query(Utente).filter(Utente.ID_Card == f"{idCard}").one().ID_Telegram


def GetIsInfinite(idTelegram: str) -> bool:
    """DATABASE_HANDLER: Ritorna se l'utente ha saldo infinito"""
    return bool(session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().isInfinite)


def InsertUser(idTelegram: str, auletta: str, genere: str, dataNascita: str, username: str) -> None:
    """DATABASE_HANDLER / ADD_USER: Inserisce l'utente con ID_Telegram ed Username passati come parametro nel DB"""

    dn = dataNascita.split("/")
    birthday = datetime.date(day=int(dn[0]),month=int(dn[1]),year=int(dn[2]))

    idAuletta : int = GetAuletta(auletta=auletta)

    utente = Utente(
        ID_Telegram=idTelegram,
        ID_Auletta=idAuletta,
        genere=genere,
        dataNascita=birthday,
        username=username,
        ID_Card=None,
        saldo=0.0,
        isAdmin=False,
        isVerified=False,
        isInfinite=False
    )

    session.add(utente)
    session.commit()

    return None

def CheckCardExists (ID_Card : str) -> bool:
    
    query = session.query(Utente).filter(Utente.ID_Card == f"{ID_Card}")
    exists = session.query(query.exists()).scalar()
    return bool(exists)

def InsertInfiniteUser(username: str, auletta: str, ID_Card: str) -> int:
    """DATABASE_HANDLER / INFINITE USER: Inserisce l'utente infinito nel DB"""
    cardExists : str = CheckCardExists(ID_Card=ID_Card)

    if cardExists is True:
        print(f"Esiste già un utente con ID_Card: {ID_Card}")
        return -1

    idAuletta : int = GetAuletta(auletta=auletta)

    telegramIDInt : int = int(GetLastInfiniteTelegramID()) + 1

    paddedID : str = str(telegramIDInt).zfill(9)

    idTelegram : str = paddedID

    utenteInfinito = Utente(
        ID_Telegram=idTelegram,
        ID_Auletta=idAuletta,
        genere="A",
        dataNascita=None,
        username=username,
        ID_Card=ID_Card,
        saldo=100,
        isAdmin=False,
        isVerified=True,
        isInfinite=True
    )

    session.add(utenteInfinito)
    session.commit()

    return 0

def GetUnverifiedUsers(idAuletta: int) -> list:
    """Ritorna la lista degli utenti non verificati afferenti all auletta con id specificato"""
    return session.query(Utente.username).filter(Utente.ID_Auletta == f"{idAuletta}", Utente.isVerified == False).all()

def GetIsAdmin(idTelegram: str) -> bool:
    """DATABASE_HANDLER: Ritorna il ruolo dell'utente"""

    return bool(session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().isAdmin)


def GetIsVerified(idTelegram: str) -> bool:
    """DATABASE_HANDLER: Ritorna se l'utente è stato approvato"""
    user: Utente = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").scalar()
    return bool(user.isVerified)


def SetIsVerified(idTelegram: str) -> int:
    """DATABASE_HANDLER: Se l'utente esiste lo setta come verificato"""

    if not CheckUserExists(idTelegram=idTelegram):
        return 1

    user: Utente = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one()
    user.isVerified = True
    session.commit()

    return 0


def DecurtaSaldo(ID_Telegram: str, saldo: float) -> None:
    user = session.query(Utente).filter(Utente.ID_Telegram == f"{ID_Telegram}").one()

    user.saldo = round(saldo, 2)

    session.commit()


def GetBalance(idTelegram: str) -> float:
    """DATABASE_HANDLER / SHOW_BALANCE: Prende il saldo dell'utente con ID_Telegram passato come parametro"""
    return session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().saldo


def getStoricoPersonale(idTelegram: str) -> list:
    """
        USER: Ritorna tuto lo storico personale
    """
    return session.query(Operazione).filter(Operazione.ID_Telegram == f"{idTelegram}").all()

def getGender(idTelegram: str) -> str:
    """
        USER: Ritorna il genere dell'utente
    """
    return session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().genere

def checkBirthday(idTelegram: str) -> bool:
    """
        USER: Ritorna vero se la data di nascita dell'utente è uguale alla data odierna
    """
    isBd = False

    dataNascita : datetime.date = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().dataNascita

    if dataNascita is None:
        return isBd

    dataCorrente : datetime.date = datetime.date.today()

    if dataNascita.day == dataCorrente.day and dataNascita.month == dataCorrente.month:
        isBd = True
    else:
        isBd = False    

    return isBd

def GetLastInfiniteTelegramID() -> str:
    """Ritorna l'ID dell'ultimo utente infinito inserito"""
    return session.query(func.Max(Utente.ID_Telegram)).filter(Utente.isInfinite == True).scalar()

# endregion

# region Aulette

def GetAulette() -> list:
    """DATABASE_HANDLER / ADD_USER: Prendiamo tutti gli id ed i nomi delle aulette"""

    return session.query(Auletta).all()


def GetAuletta(idAuletta: int) -> str:
    """DATABASE_HANDLER / ADD_USER: Dato l'ID di un'auletta, restituisce il suo nome"""

    return session.query(Auletta).filter(Auletta.ID_Auletta == f"{idAuletta}").one().Nome

def GetNomeAuletta(idAuletta: int) -> str:
    """DATABASE_HANDLER / ADD_USER: Dato l'ID di un'auletta, restituisce il suo nome"""

    return session.query(Auletta).filter(Auletta.ID_Auletta == f"{idAuletta}").one().Nome

def GetAuletta(auletta : str) -> int:
    """DATABASE_HANDLER / ADD_USER: Dato il nome dell'auletta, restituisce il suo ID"""
    
    return session.query(Auletta).filter(Auletta.Nome == f"{auletta}").one().ID_Auletta

def GetMyAuletta(idTelegram : int) -> int:
    """DATABASE_HANDLER / USER VERIFY: Dato l'id telegram dell'utente restituisce la sua auletta"""

    return session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one().ID_Auletta


def GetIdGruppiTelegramAdmin() -> list:
    """Ritorna tutti gli ID degli gruppi telegram"""
    return session.query(Auletta.ID_GruppoTelegram).all()

# endregion

# region Admin
def SetAdminDB(idTelegram: str, state: bool) -> None:
    """DATABASE_HANDLER / ADD_ADMIN: Aggiorniamo l'utente con idTelegram passato come parametro impostando
    isAdmin"""

    u: Utente = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one()
    u.isAdmin = state

    session.commit()

    return None


def getCaffeGiornalieri() -> int:
    """ADMIN: Ritorna il numero dei caffé fatti in questo giorno"""
    return session.query(Operazione).filter(func.date(Operazione.dateTimeOperazione) == datetime.date.today(),
                                            Operazione.ID_Prodotto == 1).count()


def getOperazioniGiornaliere() -> list:
    """ADMIN: Ritorna tutte le operazioni giornaliere"""
    return session.query(Operazione).filter(func.date(Operazione.dateTimeOperazione) == datetime.date.today()).all()


def incrementaSaldo(usernameBeneficiario: str, IDTelegramAmministratore: str, ricarica: float) -> int:
    """
        ADMIN: Incrementa il saldo in base alla ricarica passata come parametro
        
        Parameters:
            - usernameBeneficiario: l'username dell'utente alla quale aumentare il saldo
            - ricarica: di quanto incrementare il saldo dell'utente

        Returns:
            - 0 se l'utente non esiste
            - 1 se il saldo è stato incrementato correttamente
    """

    now: datetime.datetime = datetime.datetime.now()

    IDTelegramBeneficiario = GetIdTelegram(username=usernameBeneficiario)

    if not CheckUserExists(idTelegram=IDTelegramBeneficiario):
        return 0

    user = session.query(Utente).filter(Utente.ID_Telegram == f"{IDTelegramBeneficiario}").one()
    
    saldoRicaricato = round(user.saldo + ricarica, 2)

    r = Ricarica(
        ID_Ricarica= None,
        beneficiario=IDTelegramBeneficiario,
        amministratore=IDTelegramAmministratore,
        importo=ricarica,
        saldoPrima=user.saldo,
        saldoDopo=user.saldo + ricarica,
        dateTimeRicarica=now
    )

    user.saldo = saldoRicaricato
    session.add(r)

    session.commit()

    return 1


def getUsers() -> list:
    """
        ADMIN: Ritorna tutti gli utenti
    """
    return session.query(Utente).all()


def removeUser(idTelegram: str) -> dict:
    """
        ADMIN: Rimuove l'utente con ID_Telegram idTelegram
    """
    if not CheckUserExists(idTelegram=idTelegram):
        return {"Error": "Utente non esistente"}

    session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").delete()
    session.commit()

    return {"State": f"Utente con ID_Telegram: '{idTelegram}' cancellato!"}


def assignCard(idTelegram: str, idCard: str) -> int:
    if SetIsVerified(idTelegram=idTelegram) == 1:
        return 1  # l'utente non esiste

    # Assegnamo la card

    user: Utente = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one()
    user.ID_Card = idCard
    session.commit()

    return 0


def getIDCard(idTelegram: str) -> int:
    if SetIsVerified(idTelegram=idTelegram) == 1:
        return 1  # l'utente non esiste

    user: Utente = session.query(Utente).filter(Utente.ID_Telegram == f"{idTelegram}").one()
    card = user.ID_Card
    if card is not None:
        return int(card)
    else:
        return 0


# endregion

# region Magazzino

def QuantitaECosto(ID_Prodotto: int, ID_Auletta: int) -> Magazzino:
    """ Controllare quanto costa un elemento in una determinata auletta e controllare se esiste almeno un unità in vendita """

    result = session.query(Magazzino).filter(Magazzino.ID_Prodotto == f"{ID_Prodotto}",
                                             Magazzino.ID_Auletta == f"{ID_Auletta}").one()

    return result


def DecurtaMagazzino(idProdotto: int, idAuletta: int, quantita: int) -> dict:
    magazzino = session.query(Magazzino).filter(Magazzino.ID_Prodotto == f"{idProdotto}",
                                                Magazzino.ID_Auletta == f"{idAuletta}").one()

    if magazzino.quantita - quantita < 0:
        return {"Error": "La quantità rimanente non può essere negativa!"}

    # Siccome DePasquale è un cornuto allora questo lo commentiamo in modo tale 
    # che kaffettino non dia problemi con il magazzino
    
    # È lapalissiano nonché cristallino che a Depa pesi il culo

    # magazzino.quantita -= quantita

    # session.commit()

    return {"State": "Done"}


def GetProdotti(idAuletta: int) -> str:
    """WEB_API: Dato l'ID di un'auletta, restituisce i suoi prodotti"""

    arr = []

    class Prodotti:
        ID_Prodotto: int
        descrizione: str
        costo: float

    res = session.query(Prodotto.ID_Prodotto, Prodotto.descrizione, Magazzino.costo).join(Prodotto,
                                                                                          Prodotto.ID_Prodotto == Magazzino.ID_Prodotto).filter(
        Magazzino.ID_Auletta == idAuletta).all()

    for r in res:
        p = Prodotti()

        p.ID_Prodotto = r[0]
        p.descrizione = r[1]
        p.costo = r[2]

        arr.append(p)

    return arr


def getMagazzino(idAuletta: int) -> list:
    """
        MAGAZZINO: Ritorna tutti i prodotti e la quantità in magazzino dell'auletta con id idAuletta
    """
    return session.query(Magazzino).filter(Magazzino.ID_Auletta == f"{idAuletta}").all()


def ricaricaMagazzino(idAuletta: str, idProdotto: int, quantitaRicaricata: int) -> int:
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
        return {"Error": "Quantità ricaricata non positiva"}

    magazzino = session.query(Magazzino).filter(Magazzino.ID_Auletta == f"{idAuletta}",
                                                Magazzino.ID_Prodotto == f"{idProdotto}").one()

    magazzino.quantita = round(magazzino.quantita + quantitaRicaricata, 2)

    session.commit()

    return {"State": "Done"}


# endregion

# region Auletta

def GetDebito(ID_Auletta: int) -> float:
    """Dato l'id dell'auletta ritorna il quantitativo di debiti accumulabili"""
    return session.query(Auletta).filter(Auletta.ID_Auletta == f"{ID_Auletta}").one().DebitoMax

def GetDebitori() -> list:
    """Ritorna il nome, l'id telegram ed il saldo di tutti gli utenti che devono ancora saldare il proprio debito"""
    return session.query(Utente.ID_Telegram, Utente.username, Utente.saldo).filter(Utente.saldo < 0).all()

def GetIdGruppoTelegram(ID_Auletta: int) -> str:
    """Dato l'id dell'auletta ritorna l'id del gruppo associato"""
    return session.query(Auletta).filter(Auletta.ID_Auletta == f"{ID_Auletta}").one().ID_GruppoTelegram

# endregion

# region Operazione

def CreateOperazione(ID_Telegram: str, ID_Auletta: int, ID_Prodotto: int, costo: int) -> None:
    now: datetime.datetime = datetime.datetime.now()

    operazione = Operazione(
        ID_Operazione=None,
        ID_Telegram=ID_Telegram,
        ID_Auletta=ID_Auletta,
        ID_Prodotto=ID_Prodotto,
        dateTimeOperazione=now,
        costo=costo
    )

    session.add(operazione)
    session.commit()


# endregion

# region Wemos

# TODO: Sistemare notazione
# TODO: Fare in modo che se è in fase di testing kaffettino lo riconosca e riproduca
# una canzone diversa e nello schermo un avvertimento
def PayDB(ID_Prodotto: int, ID_Auletta: int, ID_Card: str) -> int:
    """users = session.query(Utente).all()

    return statecode"""

    """DATABASE_HANDLER / WEMOS: In base all'auletta ed all'utente, far pagare il giusto"""

    isBirthday : bool = False

    try: # Prendiamo dal magazzino il costo del prodotto

        magazzino: Magazzino = QuantitaECosto(ID_Prodotto=ID_Prodotto, ID_Auletta=ID_Auletta)
        costo = magazzino.costo

    except:
        return 3  # Prodotto con ID {ID_Prodotto} non è stato trovato nell'auletta con ID {ID_Auletta}. Oppure uno dei due non esiste completamente.

    try:
        idTelegram: str = GetIDTelegram(idCard=ID_Card)
    except:
        return 2  # Utente con idCard {ID_Card} non esistente

    # Controllare se quantità disponibile

    if magazzino.quantita <= 0:
        return 4  # Quantità dell'item inferiore a 0

    username : str = GetUsername(idTelegram=idTelegram)

    saldo: float = GetBalance(idTelegram=idTelegram)

    debito: float = GetDebito(ID_Auletta=ID_Auletta)

    # Verifica se l'utente può permettersi il prodotto
    saldoRimanente = saldo - costo

    if saldoRimanente < 0 - debito:
        return 1 # Saldo non sufficiente

    # Controlla se è il compleanno dell'utente
    isBirthday = checkBirthday(idTelegram=idTelegram) and username not in compleanniRiscattati

    # Controlla se l'utente è abilitato al saldo infinito
    isInfinite = GetIsInfinite(idTelegram=idTelegram)

    isTesting = environ.get('IS_TESTING', 'false').lower() in ('true', '1', 't')

    print(f"IS TESTING: {isTesting}")

    # Decurtatre saldo ma solo se non è compleanno
    
    if isBirthday is False and isInfinite is False and isTesting is False:
        saldo -= costo
        DecurtaSaldo(ID_Telegram=idTelegram, saldo=saldo)

    # Scalare dal magazzino un unità di quel tipo
    DecurtaMagazzino(idProdotto=ID_Prodotto, idAuletta=ID_Auletta, quantita=1)

    try:
        # Creare storico della transazione come "Eseguito"

        if isBirthday is True or isInfinite is True or isTesting:
            CreateOperazione(ID_Telegram=idTelegram, ID_Auletta=ID_Auletta, ID_Prodotto=ID_Prodotto, costo=0)
            
            if isBirthday:
                compleanniRiscattati.append(username) # Aggiungiamo il compleanno ai riscattati
        else:
            CreateOperazione(ID_Telegram=idTelegram, ID_Auletta=ID_Auletta, ID_Prodotto=ID_Prodotto, costo=costo)
            
    except:
        # Non è stato possibile creare lo storico dell'operazione avvenuta
        incrementaSaldo(username=username, ricarica=saldo)
        
        # TODO: Decommentare la riga di sotto se depa si decide ad usare il magazzino 
        # ricaricaMagazzino(idAuletta=ID_Auletta, idProdotto=ID_Prodotto, quantitaRicaricata=1)
        return 5

    returnCode = 0

    if isBirthday:
        returnCode = 69
    else:
        returnCode = 0

    return returnCode # Comprato

# endregion

#region Ricariche
def GetRecharges():
    ricariche = session.query(Ricarica).all()
    return ricariche
#endregion

#region Resoconti

def GetUsersExcel() :
    
    users = session.execute(select(Utente.ID_Telegram, Utente.ID_Card, Utente.username, Utente.saldo, Auletta.Nome, Utente.isVerified, Utente.isAdmin, Utente.isInfinite).join(Auletta, Utente.ID_Auletta == Auletta.ID_Auletta))

    return users

def GetOperazioniExcel():
    #'ID_Operazione', 'ID_Telegram', 'Username', 'Auletta', 'Descrizione', 'Costo', 'Pagato', 'DateTimeOperazione'
    operazioni = session.execute(select(Operazione.ID_Operazione, Utente.ID_Telegram, Utente.username, Auletta.Nome, Prodotto.descrizione, Magazzino.costo, Operazione.costo, Operazione.dateTimeOperazione).join(Utente, Operazione.ID_Telegram == Utente.ID_Telegram).join(Auletta, Operazione.ID_Auletta == Auletta.ID_Auletta).join(Prodotto, Operazione.ID_Prodotto == Prodotto.ID_Prodotto).join(Magazzino, Operazione.ID_Prodotto == Magazzino.ID_Prodotto).filter(func.date(Operazione.dateTimeOperazione) == datetime.date.today()).distinct())
    return operazioni 

def GetOperazioniMensiliExcel():
    #'ID_Operazione', 'ID_Telegram', 'Username', 'Auletta', 'Descrizione', 'Costo', 'Pagato', 'DateTimeOperazione'

    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    # Per ottenere l'ultimo giorno del mese, dobbiamo passare al mese successivo e poi sottrarre un giorno.
    if today.month == 12:  # Se il mese corrente è dicembre
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    end_of_month = next_month - datetime.timedelta(days=1)

    operazioni = session.execute(select(Operazione.ID_Operazione, Utente.ID_Telegram, Utente.username, Auletta.Nome, Prodotto.descrizione, Magazzino.costo, Operazione.costo, Operazione.dateTimeOperazione).join(Utente, Operazione.ID_Telegram == Utente.ID_Telegram).join(Auletta, Operazione.ID_Auletta == Auletta.ID_Auletta).join(Prodotto, Operazione.ID_Prodotto == Prodotto.ID_Prodotto).join(Magazzino, Operazione.ID_Prodotto == Magazzino.ID_Prodotto).filter(func.date(Operazione.dateTimeOperazione) >= start_of_month, func.date(Operazione.dateTimeOperazione) <= end_of_month).distinct())
    return operazioni 

def GetRicaricheExcel():
    #'R.ID_Ricarica', 'ID_Beneficiario', 'A.Username AS Beneficiario', 'R.ID_Amministratore', 'B.Username AS Amministratore', 'R.Importo', 'R.Saldo_Prima', 'R.Saldo_Dopo', 'R.Date_Time_Ricarica'

    user1 = aliased(Utente)
    user2 = aliased(Utente)

    ricariche = session.execute(select(Ricarica.ID_Ricarica, Ricarica.beneficiario.label('ID_Beneficiario'), user1.username.label('Username_Beneficiario'), Ricarica.amministratore.label('ID_Amministratore'), user2.username.label('Username_Amministratore'), Ricarica.importo, Ricarica.saldoPrima, Ricarica.saldoDopo, Ricarica.dateTimeRicarica).join(user1, Ricarica.beneficiario  == user1.ID_Telegram).join(user2, Ricarica.amministratore == user2.ID_Telegram).filter(func.date(Ricarica.dateTimeRicarica) == datetime.date.today()))
    return ricariche 

def GetRicaricheMensiliExcel():
    #'R.ID_Ricarica', 'ID_Beneficiario', 'A.Username AS Beneficiario', 'R.ID_Amministratore', 'B.Username AS Amministratore', 'R.Importo', 'R.Saldo_Prima', 'R.Saldo_Dopo', 'R.Date_Time_Ricarica'

    user1 = aliased(Utente)
    user2 = aliased(Utente)

    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    # Per ottenere l'ultimo giorno del mese, dobbiamo passare al mese successivo e poi sottrarre un giorno.
    if today.month == 12:  # Se il mese corrente è dicembre
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    end_of_month = next_month - datetime.timedelta(days=1)

    ricariche = session.execute(select(Ricarica.ID_Ricarica, Ricarica.beneficiario.label('ID_Beneficiario'), user1.username.label('Username_Beneficiario'), Ricarica.amministratore.label('ID_Amministratore'), user2.username.label('Username_Amministratore'), Ricarica.importo, Ricarica.saldoPrima, Ricarica.saldoDopo, Ricarica.dateTimeRicarica).join(user1, Ricarica.beneficiario  == user1.ID_Telegram).join(user2, Ricarica.amministratore == user2.ID_Telegram).filter(func.date(Ricarica.dateTimeRicarica) >= start_of_month, func.date(Ricarica.dateTimeRicarica) <= end_of_month))
    return ricariche 

#endregion