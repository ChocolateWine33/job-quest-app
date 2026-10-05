from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from core.db_setup import BASE
import datetime


def get_time():
    return datetime.datetime.now()

class Chat(BASE):

    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_content = Column(String, nullable=False)
    role = Column(String, nullable=False, index=True)
    date = Column(DateTime, default=get_time)
