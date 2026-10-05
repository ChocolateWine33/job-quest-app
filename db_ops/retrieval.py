from sqlalchemy.orm import Session
from models.cvs import Resume


class CvNotFoundedError (Exception):
    pass

def get_messages_by_user(db: Session, user_id: int) -> list:
    pass

def get_cv_text_by_user(db: Session, user_id: int) -> str:

    cv_text = db.query(Resume.cv_text).filter_by(user_id=user_id).scalar()

    if cv_text is None:
        raise CvNotFoundedError(f"No CV found for user ID {user_id}")
    return cv_text