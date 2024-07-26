from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Double, Boolean, Date
from sqlalchemy.orm import sessionmaker
from ..Models.Base import Base
from datetime import date

class Utente(Base):
    __tablename__ = "Utente"

    ID_Telegram = Column("ID_Telegram", CHAR(9), primary_key=True, nullable=False)
    ID_Auletta = Column("ID_Auletta", Integer, ForeignKey("Auletta.ID_Auletta"), nullable=False)
    ID_Card = Column("ID_Card", CHAR(14), nullable=True)
    username = Column("Username", String, nullable=False)
    saldo = Column("Saldo", Double, default=0.0, nullable=True)
    genere = Column("Genere", CHAR(1), default="A", nullable=True)
    dataNascita = Column("DataNascita", Date, nullable=True)
    isAdmin = Column("IsAdmin", Boolean, default=False, nullable=True)
    isVerified = Column("IsVerified", Boolean, default=False, nullable=True)
    isInfinite = Column("IsInfinite", Boolean, default=False, nullable=True)
    
    def __init__(self, ID_Telegram : str, ID_Auletta : int, ID_Card : str, username : str, saldo : Double, genere : String, dataNascita : date, isAdmin : bool, isVerified : bool, isInfinite : bool):
        self.ID_Telegram = ID_Telegram
        self.ID_Auletta = ID_Auletta
        self.ID_Card = ID_Card
        self.username = username
        self.saldo = saldo
        self.genere = genere
        self.dataNascita = dataNascita
        self.isAdmin = isAdmin
        self.isVerified = isVerified
        self.isInfinite = isInfinite

    def __repr__(self):
        return f"{self.ID_Telegram} {self.ID_Auletta} {self.ID_Card} {self.username} {self.saldo} {self.genere} {self.dataNascita} {self.isAdmin} {self.isVerified} {self.isInfinite}"