from sqlalchemy.orm import Session
from models.cvs import Resume
from models.messages import Chat


class CvNotFoundError (Exception):
    pass

CHAT_HISTORY_LIMIT = 40

def get_messages_by_user(db: Session, user_id: int) -> list:



    chat_history = (db.query(Chat)
                    .filter_by(user_id=user_id)
                    .order_by(Chat.date.desc())
                    .limit(CHAT_HISTORY_LIMIT)
                    .all()
                    )

    return chat_history.reverse()

def get_cv_text_by_user(db: Session, user_id: int) -> str:

    cv_text = db.query(Resume.cv_text).filter_by(user_id=user_id).scalar()

    if cv_text is None:
        raise CvNotFoundError(f"No CV found for user ID {user_id}")
    return cv_text

def save_message(db: Session, role: str, user_id: int, content: str):

    new_message = Chat(role=role, user_id=user_id, message_content=content)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
