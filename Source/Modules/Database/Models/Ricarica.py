from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Double, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from ..Models.Base import Base

class Ricarica(Base):
    __tablename__ = "Ricarica"

    ID_Ricarica = Column("ID_Ricarica", Integer, primary_key=True, nullable=False, autoincrement=True)
    beneficiario = Column("Beneficiario", CHAR(9), ForeignKey("Utente.ID_Telegram"), nullable=False)
    amministratore = Column("Amministratore", CHAR(9), ForeignKey("Utente.ID_Telegram"), nullable=False)
    importo = Column("Importo", Double, nullable=False)    

    def __init__(self, ID_Ricarica, beneficiario, amministratore, importo):
        self.ID_Ricarica = ID_Ricarica
        self.beneficiario = beneficiario
        self.amministratore = amministratore
        self.importo = importo

    def __repr__(self):
        return f"{self.ID_Ricarica} {self.beneficiario} {self.amministratore} {self.importo}"