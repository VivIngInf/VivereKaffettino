from Modules.Database.Models.Utente import Utente
from sqlalchemy.orm import Session  
from Modules.Database.connect import engine

session = Session(bind=engine)

daniele = Utente(
    ID_Telegram = "123456789",
    ID_Card = 1,
    username = "danieleorazio.susino",
    saldo = 0.0,
    isAdmin = True,
    isVerified = True,
)

session.add(daniele)
session.commit()