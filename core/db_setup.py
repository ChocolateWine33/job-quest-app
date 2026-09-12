from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
from config import settings

BASE = declarative_base()
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
