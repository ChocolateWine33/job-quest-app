import pytest
from sqlalchemy.orm import sessionmaker , declarative_base
from sqlalchemy import create_engine


BASE = declarative_base()
engine = create_engine("postgresql://postgres:test@localhost:5433/jobquest_test")
SessionLocal = sessionmaker(bind=engine, autoflush=True)
db = SessionLocal()

@pytest.fixture
def get_tables():
    tables = BASE.metadata.create_all(bind=engine)
    yield tables
    tables.clear()