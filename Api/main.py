from fastapi import FastAPI
from Modules.Database import TryConnect, TryDisconnect, GetAulette

app = FastAPI()

######## EVENTI ########

@app.on_event("startup")
async def startup():
    await TryConnect()

@app.on_event("shutdown")
async def shutdown():
    await TryDisconnect()

######## ROTTE ########

@app.get("/")
async def root():
    return {"message": GetAulette()}
