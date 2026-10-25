from sqlalchemy.orm import Session
from models.applications import Application
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from schemas.ai_job_assistant import ApplicationAnalysis
class DuplicateApplicationError(Exception):
    pass

class ApplicationNotFoundError(Exception):
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

def get_a_single_user_application(db: Session, user_id: int, application_id: int) -> Application:

    application = (db.query(Application)
                    .filter_by(user_id=user_id, id=application_id)
                    .first())
    if application is None:
        raise ApplicationNotFoundError()
    return application

def update_user_application(db: Session, user_id: int,
                            application_id: int,
                            status: str | None = None,
                            job_description: str | None = None) -> Application:


    current_application = (db.query(Application)
                                  .filter_by(user_id=user_id, id=application_id)
                                  .first())

    if current_application is None:
        raise ApplicationNotFoundError()

    if status is not None:
        current_application.status = status

    if job_description is not None:
        current_application.job_description = job_description

    db.commit()

    return current_application


def delete_user_application(db: Session, user_id: int, application_id: int):

    current_application = (db.query(Application)
                                      .filter_by(user_id=user_id, id=application_id)
                                      .first())
    if current_application is None:
            raise ApplicationNotFoundError()

    db.delete(current_application)
    db.commit()


def get_applications_dates(db: Session, user_id: int) -> list:

    rows = (db.query(Application.apply_date)
             .filter_by(user_id=user_id)
             .distinct()
             .order_by(Application.apply_date.desc())
             .all())

    dates = [row[0] for row in rows]

    return dates


def get_applications_data(db: Session, user_id: int) -> dict:


    rows = (
        db.query(Application.status, func.count(Application.id))
        .filter_by(user_id=user_id)
        .group_by(Application.status)
        .all()
    )

    status_counts = dict(rows)
    application_count = sum(status_counts.values())

    return{
        "application_count": application_count,
        "status_counts": status_counts
    }

def save_application_analysis(db: Session,
                              application: Application,
                              analysis: ApplicationAnalysis) -> Application:

    application.application_analysis = analysis.model_dump_json()

    db.commit()

    return application