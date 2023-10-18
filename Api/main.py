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

@app.post("/pay/{idAuletta}")
async def pay(idAuletta : int):
    return {"message": [["Auletta: ", idAuletta]]}

@app.post("/porcodue")
async def porcodue(request: Request):
    a = request.query_params['a']
    b = request.query_params['b']
    return { "message": [["a", a], ["b", b]] }


