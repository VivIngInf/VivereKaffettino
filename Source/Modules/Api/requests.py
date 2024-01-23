from pydantic import BaseModel

######## CLASSI ########

class CoffeRequest(BaseModel):
    ID_Auletta : int
    ID_Card : str
    ID_Prodotto : int

class ProdottiRequest(BaseModel):
    ID_Auletta : int

class SaldoRequest(BaseModel):
    Username : str
    Ricarica : float

class ImpostaSaldoRequest(BaseModel):
    ID_Telegram : str
    Saldo : float

class StoricoPersonaleRequest(BaseModel):
    ID_Telegram : str

class MagazzinoRequest(BaseModel):
    ID_Auletta : str

class ModificaMagazzinoRequest(BaseModel):
    ID_Auletta : str
    ID_Prodotto : int
    Ricarica : int

class DeleteUserRequest(BaseModel):
    ID_Telegram : str

class AssignCardRequest(BaseModel):
    ID_Telegram : str
    ID_Card : str