from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Double, Boolean
from sqlalchemy.orm import sessionmaker
from ..Models.Base import Base

class Utente(Base):
    __tablename__ = "Utente"

    ID_Telegram = Column("ID_Telegram", CHAR(9), primary_key=True, nullable=False)
    ID_Card = Column("ID_Card", Integer, nullable=True)
    username = Column("Username", String, nullable=False)
    saldo = Column("Saldo", Double, default=0.0, nullable=True)
    isAdmin = Column("IsAdmin", Boolean, default=False, nullable=True)
    isVerified = Column("IsVerified", Boolean, default=False, nullable=True)

    def __init__(self, ID_Telegram : str, ID_Card : int, username : str, saldo : Double, isAdmin : bool, isVerified : bool):
        self.ID_Telegram = ID_Telegram
        self.ID_Card = ID_Card
        self.username = username
        self.saldo = saldo
        self.isAdmin = isAdmin
        self.isVerified = isVerified

    def __repr__(self):
        return f"{self.ID_Telegram} {self.ID_Card} {self.username} {self.saldo} {self.isAdmin} {self.isVerified}"