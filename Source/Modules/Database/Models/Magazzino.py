from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Double, Boolean
from sqlalchemy.orm import sessionmaker
from ..Models.Base import Base

class Magazzino(Base):
    __tablename__ = "Magazzino"

    ID_Magazzino = Column("ID_Magazzino", Integer, primary_key=True, nullable=False, autoincrement=True)
    ID_Prodotto = Column("ID_Prodotto", Integer, ForeignKey("Prodotto.ID_Prodotto"), nullable=False)
    ID_Auletta = Column("ID_Auletta", Integer, ForeignKey("Auletta.ID_Auletta"), nullable=False)
    quantita = Column("Quantità", Integer, nullable=False, default=0)
    costo = Column("Costo", Double, nullable=False, default=0.0)

    def __init__(self, ID_Magazzino, ID_Prodotto, ID_Auletta, quantita, costo):
        self.ID_Magazzino = ID_Magazzino
        self.ID_Prodotto = ID_Prodotto
        self.ID_Auletta = ID_Auletta
        self.quantita = quantita
        self.costo = costo

    def __repr__(self):
        return f"{self.ID_Magazzino} {self.ID_Prodotto} {self.ID_Auletta} {self.quantita} {self.costo}"