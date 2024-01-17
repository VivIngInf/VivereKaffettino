from fastapi import FastAPI, Response
from pydantic import BaseModel
from Modules.Shared.Configs import LoadConfigs
from Modules.Shared.Query import GetAulette, PayDB, GetProdotti, getCaffeGiornalieri, getOperazioniGiornaliere, incrementaSaldo, getUsers, getStoricoPersonale, getMagazzino, ricaricaMagazzino, removeUser

app = FastAPI()

######## CLASSI ########

class CoffeRequest(BaseModel):
    ID_Auletta : int
    ID_Card : str
    ID_Prodotto : int

class ProdottiRequest(BaseModel):
    ID_Auletta : int

class IncrementaSaldoRequest(BaseModel):
    Username : str
    Ricarica : float

class StoricoPersonaleRequest(BaseModel):
    ID_Telegram : str

class MagazzinoRequest(BaseModel):
    ID_Auletta : str

class RicaricaMagazzinoRequest(BaseModel):
    ID_Auletta : str
    ID_Prodotto : int
    Ricarica : int

class DeleteUserRequest(BaseModel):
    ID_Utente : str

######## EVENTI ########

@app.on_event("startup")
async def startup():
    #await LoadConfigs()
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

######## ROTTE ########

@app.get("/aulette")
async def aulette():
    return GetAulette()

@app.post("/prodotti")
async def prodotti(pRequest: ProdottiRequest):
    return GetProdotti(pRequest.ID_Auletta)

@app.post("/pay")
async def pay(cRequest: CoffeRequest):
    return PayDB(ID_Prodotto=cRequest.ID_Prodotto, ID_Auletta=cRequest.ID_Auletta, ID_Card=cRequest.ID_Card)

@app.post("/incrementaSaldo")
async def incrementaS(incRequest: IncrementaSaldoRequest):
    return incrementaSaldo(username=incRequest.Username, ricarica=incRequest.Ricarica)

@app.post("/storicoPersonale")
async def storicoPersonale(storicoRequest: StoricoPersonaleRequest):
    return getStoricoPersonale(storicoRequest.ID_Telegram)

@app.post("/ricaricaMagazzino")
async def ricaricaM(magazzinoRequest: RicaricaMagazzinoRequest):
    return ricaricaMagazzino(magazzinoRequest.ID_Auletta, magazzinoRequest.ID_Prodotto, magazzinoRequest.Ricarica)

@app.post("/visualizzaMagazzino")
async def visualizzaMagazzino(magazzinoRequest: MagazzinoRequest):
    return getMagazzino(magazzinoRequest.ID_Auletta)

@app.post("/rimuoviUtente")
async def rimuoviUtente(magazzinoRequest: MagazzinoRequest):
    return removeUser(magazzinoRequest.ID_Auletta)

@app.get("/caffeGiornalieri")
async def caffeGiornalieri(deleteUserRequest : DeleteUserRequest):
    return getCaffeGiornalieri(deleteUserRequest.ID_Utente)

@app.get("/operazioniGiornaliere")
async def operazioniGiornaliere():
    return getOperazioniGiornaliere()

@app.get("/getUsers")
async def users():
    return getUsers()