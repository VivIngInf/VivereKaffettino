from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Double, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from ..Models.Base import Base

class Ricarica(Base):
    __tablename__ = "Ricarica"

    ID_Ricarica = Column("ID_Ricarica", Integer, primary_key=True, nullable=False, autoincrement=True)
    beneficiario = Column("Beneficiario", CHAR(9), ForeignKey("Utente.ID_Telegram"), nullable=False)
    amministratore = Column("Amministratore", CHAR(9), ForeignKey("Utente.ID_Telegram"), nullable=False)
    importo = Column("Importo", Double, nullable=False)    
    saldoPrima = Column("Saldo_Prima", Double, nullable=False)
    saldoDopo = Column("Saldo_Dopo", Double, nullable=False)
    dateTimeRicarica = Column("Date_Time_Ricarica", DateTime, nullable=False)

    def __init__(self, ID_Ricarica : int, beneficiario : str, amministratore : str, importo : Double, saldoPrima : Double, saldoDopo : Double, dateTimeRicarica : DateTime):
        self.ID_Ricarica = ID_Ricarica
        self.beneficiario = beneficiario
        self.amministratore = amministratore
        self.importo = importo
        self.saldoPrima = saldoPrima
        self.saldoDopo = saldoDopo
        self.dateTimeRicarica = dateTimeRicarica

    def __repr__(self):
        return f"{self.ID_Ricarica} {self.beneficiario} {self.amministratore} {self.importo} {self.saldoPrima} {self.saldoDopo} {self.dateTimeRicarica}"