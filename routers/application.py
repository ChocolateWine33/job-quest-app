from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.user import User
from core.db_setup import get_db
from core.security import get_current_user
from db_ops.application_tracker import add_application, get_user_applications, DuplicateApplicationError
from schemas.application import ApplicationResponse, JobApplication

router = APIRouter(tags=["Application Tracker"])


@router.post("/add_application", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def add_application_route(job_application: JobApplication,
                           db: Session = Depends(get_db),
                           user: User = Depends(get_current_user)):

    try:
        return add_application(db=db,user_id=user.id,company_name=job_application.company_name,role=job_application.role)
    except DuplicateApplicationError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.get("/get_applications", response_model=list[ApplicationResponse])
def get_applications(db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):

    applications = get_user_applications(user_id=user.id, db=db)
    return applications


@router.put("/update_application_status/{application_id}")
def update_application_status(db: Session = Depends(get_db),
                            user: User = Depends(get_current_user)):
    pass
