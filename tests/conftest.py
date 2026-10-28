import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from core.db_setup import BASE , get_db
from main import app



engine = create_engine("postgresql://postgres:test@localhost:5433/jobquest_test")
SessionLocal = sessionmaker(bind=engine, autoflush=True)


@pytest.fixture
def setup_database():
    BASE.metadata.create_all(bind=engine)
    yield 
    BASE.metadata.drop_all(bind=engine)

@pytest.fixture
def client(setup_database):           # asking for setup_database makes pytest run it first

    def override_get_db():
        db = SessionLocal()                      # a session from the TEST SessionLocal
        try:
            yield db
        finally:
            db.close()
                # same cleanup as your real get_db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()  # undo the override after the test
