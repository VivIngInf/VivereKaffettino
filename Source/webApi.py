from fastapi import FastAPI, Response
from pydantic import BaseModel
from Modules.Shared.Configs import LoadConfigs
from Modules.Shared.Query import GetAulette, PayDB, GetProdotti

app = FastAPI()

######## CLASSI ########

class CoffeRequest(BaseModel):
    ID_Auletta : int
    ID_Card : str
    ID_Prodotto : int

class ProdottiRequest(BaseModel):
    ID_Auletta : int

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