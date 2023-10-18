from fastapi import FastAPI
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

@app.get("/")
async def root():
    return {"message": GetAulette()}
