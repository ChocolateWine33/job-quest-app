from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Date, ForeignKey, UniqueConstraint
from core.db_setup import BASE
import datetime


def get_date():
    return datetime.date.today()

class Application(BASE):

    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String, nullable=False)
    apply_date = Column(Date, default=get_date)
    role_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Applied")


    __table_args__ = (
    UniqueConstraint('company_name', 'user_id', 'role_name', name='unique_role_per_company_per_user'),
)