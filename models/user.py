from sqlalchemy import Column, String, Integer, Date
from core.db_setup import BASE
import datetime

def get_date():
    return datetime.date.today()

class User(BASE):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    joined_date = Column(Date, default=get_date)
    cv_url = Column(String, nullable=True)

