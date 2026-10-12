from sqlalchemy.orm import Session
from models.applications import Application
from sqlalchemy.exc import IntegrityError

class DuplicateApplicationError(Exception):
    pass

def add_application(user_id: int,
                    company_name: str,
                    role: str,
                    db: Session) -> Application:

    existing_application = db.query(Application).filter_by(user_id=user_id, company_name=company_name, role_name=role).first()
    if existing_application:
        raise DuplicateApplicationError("You have already submitted this application!")

    new_application = Application(company_name=company_name, role_name=role, user_id=user_id)

    db.add(new_application)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateApplicationError("You have already submitted this application!"
    ) from exc

    db.refresh(new_application)
    return new_application

def get_user_applications(db: Session, user_id: int) -> list:

    applications = (db.query(Application)
                    .filter_by(user_id=user_id)
                    .order_by(Application.apply_date.asc())
                    .all())
    return applications


