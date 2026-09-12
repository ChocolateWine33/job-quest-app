from fastapi import FastAPI
from core.db_setup import BASE, engine
from routers import authentication

BASE.metadata.create_all(bind=engine)

app = FastAPI(title="Job Quest") 

app.include_router(authentication.router)


@app.get("/")
def root():
    return {"message": "Job Quest is Running!"}