from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.user import User
from core.db_setup import get_db
from core.security import get_current_user
from db_ops.application_tracker import add_application, get_user_applications, update_user_application, delete_user_application, get_applications_dates, get_applications_data, DuplicateApplicationError,ApplicationNotFoundError
from schemas.application import ApplicationResponse, JobApplication, ApplicationStatusUpdate
from services.gamification import build_progress


router = APIRouter(tags=["Application Tracker"])


@router.post("/add_application", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def add_application_route(job_application: JobApplication,
                           db: Session = Depends(get_db),
                           user: User = Depends(get_current_user)):


    try:
        return add_application(db=db,user_id=user.id,company_name=job_application.company_name,role=job_application.role, job_description=job_application.job_description)
    except DuplicateApplicationError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.get("/progress")
def get_progress(db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):

    dates = get_applications_dates(db=db, user_id=user.id)
    user_data = get_applications_data(db=db, user_id=user.id)

    return build_progress(user_data["application_count"], user_data["status_counts"], dates, user.id)


@router.get("/get_applications", response_model=list[ApplicationResponse])
def get_applications(db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):

    applications = get_user_applications(user_id=user.id, db=db)
    return applications


@router.patch("/update_application_status/{application_id}", response_model=ApplicationResponse)
def update_application_status(application_id: int,
                              update: ApplicationStatusUpdate,
                              db: Session = Depends(get_db),
                            user: User = Depends(get_current_user),):
    try:
        application = update_user_application(db=db, user_id=user.id, application_id=application_id, status=update.status.value)
        return application
    except ApplicationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("We couldn't find that application, Please Try again!")
        )

@router.delete("/delete_application/{application_id}")
def delete_application(application_id: int,
                        db: Session = Depends(get_db),
                        user: User = Depends(get_current_user),):

    try:
        delete_user_application(db=db, user_id=user.id, application_id=application_id)
    except ApplicationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("We couldn't find that application, Please Try again!")
        )

    return {"message": "Application deleted successfully."}



