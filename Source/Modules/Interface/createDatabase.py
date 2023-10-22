from Modules.Database.Models.Auletta import Auletta
from Modules.Database.Models.Magazzino import Magazzino
from Modules.Database.Models.Operazione import Operazione
from Modules.Database.Models.Prodotto import Prodotto
from Modules.Database.Models.Ricarica import Ricarica
from Modules.Database.Models.Rifornimento import Rifornimento
from Modules.Database.Models.Utente import Utente
from Modules.Database.Models.Base import Base
from Modules.Database.connect import engine

# Siccome tutti i modelli generano da Base,
# possiamo invocare la generazione di base
# e tutti i modelli verranno generati
def CreateAll():
    Base.metadata.create_all(bind=engine)