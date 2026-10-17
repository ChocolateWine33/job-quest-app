from fastapi import FastAPI
from core.db_setup import BASE, engine
from routers import authentication, upload, ai_assistant, application

BASE.metadata.create_all(bind=engine)

app = FastAPI(title="Job Quest")

app.include_router(authentication.router)
app.include_router(upload.router)
app.include_router(ai_assistant.router)
app.include_router(application.router)
@app.get("/")
def root():
    return {"message": "Job Quest is Running!"}
