from fastapi import FastAPI, Request, Response
from Modules.Shared.Query import GetAulette, PayDB, GetProdotti, getCaffeGiornalieri, getOperazioniGiornaliere, incrementaSaldo, getUsers, getStoricoPersonale, getMagazzino, ricaricaMagazzino, removeUser, DecurtaMagazzino, DecurtaSaldo, assignCard, GetRecharges, InsertInfiniteUser, GetProdottiNonAssociati
from Modules.Api.requests import CoffeRequest, SaldoRequest, ProdottiRequest, MagazzinoRequest, DeleteUserRequest, ImpostaSaldoRequest, StoricoPersonaleRequest, ModificaMagazzinoRequest, AssignCardRequest, InfiniteUserRequest
from dotenv import load_dotenv, find_dotenv
from os import environ

app = FastAPI()

#region Middleware

token : str | None = ""
invalidTokenResponse : Response = Response(content="Unauthorized", status_code=401)

def LoadConfigs() -> None:
    global token
    load_dotenv(find_dotenv()) # Carichiamo il file di ambiente dove sono stati salvati i file di config
    token = environ.get("SECRET_API")
    pass

@app.middleware("http")
async def myAuth(request: Request, call_next):

    s = request.headers.get("X-Secret")

    if s is None:
        return invalidTokenResponse

    if s != token:
        return invalidTokenResponse
    
    response = await call_next(request)
    
    return response

#endregion

#region Events

@app.on_event("startup")
async def startup():
    LoadConfigs()
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

@app.get("/getRicariche")
async def getRicariche():
    return GetRecharges()

#endregion routes

#region Post Routes

@app.post("/getProdottiNotInAuletta")
async def getProdottiNotInAuletta(request: ProdottiRequest):
    return GetProdottiNonAssociati(request.ID_Auletta)

@app.post("/prodotti")
async def prodotti(request: ProdottiRequest):
    return GetProdotti(request.ID_Auletta)

@app.post("/pay")
async def pay(request: CoffeRequest):
    return PayDB(ID_Prodotto=request.ID_Prodotto, ID_Auletta=request.ID_Auletta, ID_Card=request.ID_Card)

@app.post("/incrementaSaldo")
async def incrementaS(request: SaldoRequest):
    return incrementaSaldo(usernameBeneficiario=request.UsernameBeneficiario, IDTelegramAmministratore=request.IDTelegramAmministratore, ricarica=request.Ricarica)

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

@app.post("/newInfiniteUser")
async def newInfiniteUser(request : InfiniteUserRequest):
    exitCode : int = InsertInfiniteUser(request.Username, request.NomeAuletta, request.ID_Card)
    
    return {"Status" : "Utente creato" if exitCode is 0 else "Card già esistente!"}


#endregion