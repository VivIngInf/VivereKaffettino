from fastapi import FastAPI
from Modules.Shared.Configs import LoadConfigs
from Modules.Shared.Query import GetAulette, PayDB, GetProdotti, getCaffeGiornalieri, getOperazioniGiornaliere, incrementaSaldo, getUsers, getStoricoPersonale, getMagazzino, ricaricaMagazzino, removeUser, DecurtaMagazzino, DecurtaSaldo, assignCard
from Modules.Api.requests import CoffeRequest, SaldoRequest, ProdottiRequest, MagazzinoRequest, DeleteUserRequest, ImpostaSaldoRequest, StoricoPersonaleRequest, ModificaMagazzinoRequest, AssignCardRequest

app = FastAPI()

#region Events

@app.on_event("startup")
async def startup():
    #await LoadConfigs()
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

#endregion

#region Get Routes

@app.get("/aulette")
async def aulette():
    return GetAulette()

@app.get("/caffeGiornalieri")
async def caffeGiornalieri():
    return getCaffeGiornalieri()

@app.get("/operazioniGiornaliere")
async def operazioniGiornaliere():
    return getOperazioniGiornaliere()

@app.get("/getUsers")
async def users():
    return getUsers()

#endregion routes

#region Post Routes

@app.post("/prodotti")
async def prodotti(request: ProdottiRequest):
    return GetProdotti(request.ID_Auletta)

@app.post("/pay")
async def pay(request: CoffeRequest):
    return PayDB(ID_Prodotto=request.ID_Prodotto, ID_Auletta=request.ID_Auletta, ID_Card=request.ID_Card)

@app.post("/incrementaSaldo")
async def incrementaS(request: SaldoRequest):
    return incrementaSaldo(username=request.Username, ricarica=request.Ricarica)

@app.post("/impostaSaldo")
async def impostS(request: ImpostaSaldoRequest):
    return DecurtaSaldo(ID_Telegram=request.ID_Telegram, saldo=request.Saldo)

@app.post("/storicoPersonale")
async def storicoPersonale(request: StoricoPersonaleRequest):
    return getStoricoPersonale(request.ID_Telegram)

@app.post("/ricaricaMagazzino")
async def ricaricaM(request: ModificaMagazzinoRequest):
    return ricaricaMagazzino(request.ID_Auletta, request.ID_Prodotto, request.Ricarica)

@app.post("/decurtaMagazzino")
async def decurtaM(request: ModificaMagazzinoRequest):
    return DecurtaMagazzino(idProdotto=request.ID_Prodotto, idAuletta=request.ID_Auletta, quantita=request.Ricarica)

@app.post("/visualizzaMagazzino")
async def visualizzaMagazzino(request: MagazzinoRequest):
    return getMagazzino(request.ID_Auletta)

@app.post("/rimuoviUtente")
async def rimuoviUtente(request : DeleteUserRequest):
    return removeUser(request.ID_Telegram)

@app.post("/assegnaCard")
async def assegnaCard(request : AssignCardRequest):
    return assignCard(request.ID_Telegram, request.ID_Card)

#endregion