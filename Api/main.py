from fastapi import FastAPI
from Modules.Configs import LoadConfigs
from Modules.Database import GetAulette
from pydantic import BaseModel

app = FastAPI()

######## CLASSI ########

class CoffeRequest(BaseModel):
    ID_Auletta : int
    ID_Utente : int


######## EVENTI ########

@app.on_event("startup")
async def startup():
    await LoadConfigs()

@app.on_event("shutdown")
async def shutdown():
    pass

######## ROTTE ########

@app.post("/gigibarba")
async def gigibarba():
    return { "ID_Auletta" : cRequest.ID_Auletta, "ID_Utente" : cRequest.ID_Utente}

@app.post("/pay")
async def pay(cRequest: CoffeRequest):
    user : str = cRequest.query_params['ID_Utente']
    auletta : str = cRequest.query_params['ID_Auletta']

    if user == None or auletta == None:
        return {"Error:" "Uno dei due parametri era nullo!"}

    return {"ID_Utente": user, "ID_Auletta": auletta}