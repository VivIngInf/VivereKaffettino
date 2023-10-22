from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Double, Boolean
from sqlalchemy.orm import sessionmaker
from ..Models.Base import Base

class Auletta(Base):
    __tablename__ = "Auletta"

    ID_Auletta = Column("ID_Auletta", Integer, primary_key=True, nullable=False, autoincrement=True)
    Nome = Column("Nome", String, nullable=False)
    DebitoMax = Column("DebitoMax", Integer, nullable=False, default=0)
    ID_GruppoTelegram = Column("ID_GruppoTelegram", CHAR(13), nullable=True)

    def __init__(self, ID_Auletta : int, Nome : str, DebitoMax : int, ID_GruppoTelegram : str):
        self.ID_Auletta = ID_Auletta
        self.Nome = Nome
        self.DebitoMax = DebitoMax
        self.ID_GruppoTelegram = ID_GruppoTelegram

    def __repr__(self):
        return f"{self.ID_Auletta} {self.Nome} {self.DebitoMax} {self.ID_GruppoTelegram}"