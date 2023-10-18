from fastapi import FastAPI, Request
from Modules.Configs import LoadConfigs
from Modules.Database import GetAulette


app = FastAPI()
######## EVENTI ########

@app.on_event("startup")
async def startup():
    await LoadConfigs()

@app.on_event("shutdown")
async def shutdown():
    pass

######## ROTTE ########

@app.post("/suca")
async def suca():
    return {"message": "milla"}

@app.post("/pay")
async def pay(request : Request):
    if len(request.query_params) < 2:
        return { "Error:": "Non hai inserito abbastanza parametri"}

    user : int = request.query_params['ID_Utente']
    auletta : int = request.query_params['ID_Auletta']

    if user == None or auletta == None:
        return {"Error:" "Uno dei due parametri era nullo!"}

    return {"messageUser": user, "messageAuletta": auletta}