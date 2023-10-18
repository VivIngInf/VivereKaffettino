from fastapi import FastAPI
from Modules.Configs import LoadConfigs
from Modules.Database import GetAulette, PayDB
from pydantic import BaseModel

app = FastAPI()

######## CLASSI ########

class CoffeRequest(BaseModel):
    ID_Auletta : int
    ID_Utente : int
    ID_Prodotto : int


######## EVENTI ########

@app.on_event("startup")
async def startup():
    await LoadConfigs()

@app.on_event("shutdown")
async def shutdown():
    pass

######## ROTTE ########

@app.post("/pay")
async def pay(cRequest: CoffeRequest):
    return PayDB(ID_Prodotto=cRequest.ID_Prodotto, ID_Auletta=cRequest.ID_Auletta, ID_Card=cRequest.ID_Utente)