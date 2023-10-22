from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Double, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from ..Models.Base import Base

class Rifornimento(Base):
    __tablename__ = "Rifornimento"

    ID_RifornimentoID_Rifornimento = Column("ID_Rifornimento", Integer, primary_key=True, nullable=False, autoincrement=True)
    ID_Telegram = Column("ID_Telegram", CHAR(9), ForeignKey("Utente.ID_Telegram"), nullable=False)
    ID_Auletta = Column("ID_Auletta", Integer, ForeignKey("Auletta.ID_Auletta"), nullable=False)
    ID_Prodotto = Column("ID_Prodotto", Integer, ForeignKey("Prodotto.ID_Prodotto"), nullable=False)
    dataOraRifornimento = Column("DataOraRifornimento", DateTime, nullable=False)    
    quantita = Column("Quantita", Integer, nullable=False)    
    costo = Column("Costo", Double, nullable=False)        

    def __init__(self, ID_Rifornimento, ID_Telegram, ID_Auletta, ID_Prodotto, dataOraRifornimento, quantita, costo):
        self.ID_Rifornimento = ID_Rifornimento
        self.ID_Telegram = ID_Telegram
        self.ID_Auletta = ID_Auletta
        self.ID_Prodotto = ID_Prodotto
        self.dataOraRifornimento = dataOraRifornimento
        self.quantita = quantita
        self.costo = costo

    def __repr__(self):
        return f"{self.ID_Rifornimento} {self.ID_Telegram} {self.ID_Auletta} {self.ID_Prodotto} {self.dataOraRifornimento} {self.quantita} {self.costo}"