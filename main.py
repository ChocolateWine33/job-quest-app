from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.db_setup import BASE, engine
from routers import authentication, upload, ai_assistant
from routers import application as application_router
import os

BASE.metadata.create_all(bind=engine)

app = FastAPI(title="Job Quest")

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication.router)
app.include_router(upload.router)
app.include_router(ai_assistant.router)
app.include_router(application_router.router)
@app.get("/")
def root():
    return {"message": "Job Quest is Running!"}
