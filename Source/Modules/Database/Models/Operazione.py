from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Double, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from ..Models.Base import Base

class Operazione(Base):
    __tablename__ = "Operazione"

    ID_Operazione = Column("ID_Magazzino", Integer, primary_key=True, nullable=False, autoincrement=True)
    ID_Telegram = Column("ID_Telegram", CHAR(9), ForeignKey("Utente.ID_Telegram"), nullable=False)
    ID_Auletta = Column("ID_Auletta", Integer, ForeignKey("Auletta.ID_Auletta"), nullable=False)
    ID_Prodotto = Column("ID_Prodotto", Integer, ForeignKey("Prodotto.ID_Prodotto"), nullable=False)
    dateTimeOperazione = Column("DateTimeOperazione", DateTime, nullable=False)
    costo = Column("Costo", Double, nullable=False)

    def __init__(self, ID_Operazione, ID_Telegram, ID_Auletta, ID_Prodotto, dateTimeOperazione, costo):
        self.ID_Operazione = ID_Operazione
        self.ID_Telegram = ID_Telegram
        self.ID_Auletta = ID_Auletta
        self.ID_Prodotto = ID_Prodotto
        self.dateTimeOperazione = dateTimeOperazione
        self.costo = costo

    def __repr__(self):
        return f"{self.ID_Operazione} {self.ID_Telegram} {self.ID_Auletta} {self.ID_Prodotto} {self.dateTimeOperazione} {self.costo}"