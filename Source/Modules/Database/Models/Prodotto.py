from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Double, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from ..Models.Base import Base

class Prodotto(Base):
    __tablename__ = "Prodotto"

    ID_Prodotto = Column("ID_Prodotto", Integer, primary_key=True, nullable=False, autoincrement=True)
    descrizione = Column("Descrizione", CHAR(50), nullable=False)

    def __init__(self, ID_Prodotto : int, descrizione : str):
        self.ID_Prodotto = ID_Prodotto
        self.descrizione = descrizione

    def __repr__(self):
        return f"{self.ID_Prodotto} {self.descrizione}"