from Modules.Database.Models.Utente import Utente
from Modules.Database.Models.Auletta import Auletta
from Modules.Database.Models.Prodotto import Prodotto
from Modules.Database.Models.Magazzino import Magazzino
from Modules.Shared.Session import session
from Modules.Database.connect import engine

from datetime import date

def CreatePersistent():

    #region Aulette

    ingegneria = Auletta(
        ID_Auletta=1,
        Nome="Ingegneria - ED. 8",
        DebitoMax=3,
        ID_GruppoTelegram="-1002059887014"
    )

    deim = Auletta(
        ID_Auletta=2,
        Nome="Ingegneria - DEIM",
        DebitoMax=3,
        ID_GruppoTelegram="-1002059887014"
    )

    session.add(ingegneria)
    session.add(deim)

    #endregion

    #region Prodotto

    caffe = Prodotto(
        ID_Prodotto=1,
        descrizione="Caffe'"
    )

    acqua = Prodotto(
        ID_Prodotto=2,
        descrizione="Acqua"
    )

    te = Prodotto(
        ID_Prodotto=3,
        descrizione="Tè"
    )

    gelato = Prodotto(
        ID_Prodotto=4,
        descrizione="Gelato"
    )

    session.add(caffe)
    session.add(acqua)
    session.add(te)
    session.add(gelato)

    #endregion

    #region Magazzino
    caffeIngegneria = Magazzino(
        ID_Magazzino=1,
        ID_Prodotto=1,
        ID_Auletta=1,
        quantita=100,
        costo=0.4
    )

    acquaIngegneria = Magazzino(
        ID_Magazzino=2,
        ID_Prodotto=2,
        ID_Auletta=1,
        quantita=100,
        costo=0.4
    )
    
    gelatoIngegneria = Magazzino(
        ID_Magazzino=5,
        ID_Prodotto=4,
        ID_Auletta=1,
        quantita=100,
        costo=1.0
    )

    caffeDeim = Magazzino(
        ID_Magazzino=3,
        ID_Prodotto=1,
        ID_Auletta=2,
        quantita=100,
        costo=0.4
    )

    teDeim = Magazzino(
        ID_Magazzino=4,
        ID_Prodotto=3,
        ID_Auletta=2,
        quantita=100,
        costo=0.6
    )

    session.add(caffeIngegneria)
    session.add(acquaIngegneria)
    session.add(caffeDeim)
    session.add(teDeim)
    session.add(gelatoIngegneria)

    #endregion

    #region Utente

    aulettaIngegneria = Utente(
        ID_Telegram = "000000000",
        ID_Auletta = 1,
        ID_Card = "2091883115",
        username = "Auletta.Ingegneria",
        genere="A",
        dataNascita=None,
        saldo = 9999999.0,
        isAdmin = False,
        isVerified = True,
    )

    riccardo = Utente(
        ID_Telegram = "188128674",
        ID_Auletta = 1,
        ID_Card = "42044823011200",
        username = "Riccardo.Sciacca",
        genere="M",
        dataNascita=date(2001, 1, 18),
        saldo = 0,
        isAdmin = True,
        isVerified = True
    )

    daniele = Utente(
        ID_Telegram = "752154717",
        ID_Auletta = 1,
        ID_Card = "1",
        username = "DanieleOrazio.Susino",
        genere="M",
        dataNascita=date(2003, 11, 17),
        saldo = 0,
        isAdmin = True,
        isVerified = True,
    )

    andreaDePasquale = Utente(
        ID_Telegram= "154366501",
        ID_Auletta= 1,
        ID_Card= "425116123111200",
        username="Andrea.Depasquale",
        genere="M",
        dataNascita=date(2001, 7, 17),
        saldo = 0,
        isAdmin = True,
        isVerified = True,
    )

    session.add(aulettaIngegneria)

    session.add(riccardo)

    session.add(daniele)

    session.add(andreaDePasquale)

    #endregion

    session.commit()