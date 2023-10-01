from fastapi import FastAPI
from Modules.Database import TryConnect, TryDisconnect, GetAulette
from Modules.Configs import LoadConfigs

app = FastAPI()

######## EVENTI ########

@app.on_event("startup")
async def startup():
    await LoadConfigs()

@app.on_event("shutdown")
async def shutdown():
    pass

######## ROTTE ########

@app.get("/")
async def root():
    return {"message": GetAulette()}
