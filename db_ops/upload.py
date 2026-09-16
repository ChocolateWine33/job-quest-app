from sqlalchemy.orm import Session
from models.user import User
from db_ops.user import UserNotFoundError

def save_cv_url(db: Session, user_id: int, cv_url: str):

    current_user = db.query(User).filter_by(id=user_id).one_or_none()
    if not current_user:
        raise UserNotFoundError(id=user_id)

    current_user.cv_url = cv_url
    db.commit()
    db.refresh(current_user)
