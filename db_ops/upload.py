from sqlalchemy.orm import Session
from models.user import User
from models.cvs import Resume
from db_ops.user import UserNotFoundError
from core.config import supabase

def save_cv_url(db: Session, user_id: int, cv_url: str):

    current_user = db.query(User).filter_by(id=user_id).one_or_none()
    if not current_user:
        raise UserNotFoundError(id=user_id)

    old_cv_url = current_user.cv_url
    current_user.cv_url = cv_url
    db.commit()
    db.refresh(current_user)
    if old_cv_url:
        old_filename = old_cv_url.split("/")[-1]
        try:
            supabase.storage.from_("resumes").remove([old_filename])
        except Exception:
            pass

def save_cv_text(db:Session, user_id: int, cv_text: str) -> Resume:

    existing_cv_text = db.query(Resume).filter_by(user_id=user_id).one_or_none()

    if existing_cv_text:
        existing_cv_text.cv_text = cv_text
        resume = existing_cv_text
    else:
        resume = Resume(user_id=user_id, cv_text=cv_text)
        db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume



