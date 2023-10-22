from Modules.Database.Models.Utente import Utente
from Modules.Database.Models.Auletta import Auletta
from Modules.Database.Models.Base import Base
from Modules.Database.connect import engine

# Siccome tutti i modelli generano da Base,
# possiamo invocare la generazione di base
# e tutti i modelli verranno generati

Base.metadata.create_all(bind=engine)