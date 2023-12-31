from Modules.Database.Models.Utente import Utente
from Modules.Database.Models.Auletta import Auletta
from Modules.Database.Models.Prodotto import Prodotto
from Modules.Database.Models.Magazzino import Magazzino
from Modules.Shared.Session import session
from Modules.Database.connect import engine

def CreatePersistent():

    #region Utente

    guest = Utente(
        ID_Telegram = "000000000",
        ID_Card = "1",
        username = "guest",
        saldo = 9999999.0,
        isAdmin = False,
        isVerified = True,
    )

    riccardo = Utente(
        ID_Telegram = "188128674",
        ID_Card = "48213022911200",
        username = "Riccardo.Sciacca",
        saldo = 100.0,
        isAdmin = True,
        isVerified = True
    )

    daniele = Utente(
        ID_Telegram = "752154717",
        ID_Card = "1",
        username = "DanieleOrazio.Susino",
        saldo = 500.0,
        isAdmin = True,
        isVerified = True,
    )

    session.add(guest)

    session.add(riccardo)

    session.add(daniele)

    #endregion

    #region Aulette

    ingegneria = Auletta(
        ID_Auletta=1,
        Nome="Ingegneria",
        DebitoMax=3,
        ID_GruppoTelegram=""
    )

    deim = Auletta(
        ID_Auletta=2,
        Nome="Deim",
        DebitoMax=3,
        ID_GruppoTelegram=""
    )

    session.add(ingegneria)
    session.add(deim)

    #endregion

    #region Prodotto

    caffe = Prodotto(
        ID_Prodotto=1,
        descrizione="Caffè"
    )

    acqua = Prodotto(
        ID_Prodotto=2,
        descrizione="Acqua"
    )

    te = Prodotto(
        ID_Prodotto=3,
        descrizione="Tè"
    )

    session.add(caffe)
    session.add(acqua)
    session.add(te)

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
        quantita=33,
        costo=0.3
    )
    
    caffeDeim = Magazzino(
        ID_Magazzino=3,
        ID_Prodotto=1,
        ID_Auletta=2,
        quantita=50,
        costo=0.4
    )

    teDeim = Magazzino(
        ID_Magazzino=4,
        ID_Prodotto=3,
        ID_Auletta=2,
        quantita=80,
        costo=0.6
    )

    session.add(caffeIngegneria)
    session.add(acquaIngegneria)
    session.add(caffeDeim)
    session.add(teDeim)

    #endregion

    session.commit()