from sqlalchemy import Column, String, Integer, Date, ForeignKey
from core.db_setup import BASE


class Resume(BASE):

    __tablename__ = "cvs"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cv_text = Column(String, nullable=False)

