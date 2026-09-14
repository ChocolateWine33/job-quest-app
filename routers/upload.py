from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from sqlalchemy.orm import Session
from core.db_setup import get_db
from core.security import get_current_user
from models.user import User
import uuid



router = APIRouter(tags=["Upload"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_route(cv_file: UploadFile = File(...),
                    db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):


    file_bytes = await cv_file.read()

    # Generate a unique filename (cv_<user_id>_<uuid>.pdf)
    file_extension = cv_file.filename.split(".")[-1]
    unique_filename = f"cv_{user.id}_{uuid.uuid4().hex}.{file_extension}"