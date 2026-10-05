from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from sqlalchemy.orm import Session
from core.db_setup import get_db
from core.security import get_current_user
from models.user import User
from services.file_service import save_file, extract_text_from_url
from db_ops.upload import save_cv_url, save_cv_text, UserNotFoundError

router = APIRouter(tags=["Upload"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_route(cv_file: UploadFile = File(...),
                    db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):

    cv_public_url = save_file(cv_file=cv_file, user_id=user.id)
    cv_text = extract_text_from_url(cv_url=cv_public_url)
    
    try:
        save_cv_url(db=db, user_id=user.id, cv_url=cv_public_url)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User Not Found!")

    save_cv_text(db=db, user_id=user.id, cv_text=cv_text)
    
    return {
        "message": "CV Uploaded Successfully",
        "cv_url": cv_public_url
    }
