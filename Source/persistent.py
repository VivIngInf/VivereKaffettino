from Modules.Database.Models.Utente import Utente
from Modules.Database.Models.Auletta import Auletta
from Modules.Database.Models.Prodotto import Prodotto
from Modules.Database.Models.Magazzino import Magazzino
from Modules.Shared.Session import session
from Modules.Database.connect import engine

#region Utente

daniele = Utente(
    ID_Telegram = "123456789",
    ID_Card = 1,
    username = "danieleorazio.susino",
    saldo = 0.0,
    isAdmin = True,
    isVerified = True,
)

ivan = Utente(
    ID_Telegram = "987654321",
    ID_Card = 2,
    username = "ivan.sollazzo",
    saldo = 10.0,
    isAdmin = False,
    isVerified = True,
)

session.add(daniele)
session.add(ivan)

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

caffe = Prodotto(
    ID_Prodotto=2,
    descrizione="Acqua"
)

caffe = Prodotto(
    ID_Prodotto=3,
    descrizione="Tè"
)

session.add(caffe)

#endregion

#region Magazzino
caffeIngegneria = Magazzino(
    ID_Magazzino=1,
    ID_Prodotto=1,
    ID_Auletta=1,
    quantita=100,
    costo=0.4
)

session.add(caffeIngegneria)

#endregion

session.commit()