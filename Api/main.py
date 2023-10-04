from fastapi import FastAPI

app = FastAPI()

######## EVENTI ########

@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

######## ROTTE ########

@app.get("/")
async def root():
    return {"message": "suca"}
