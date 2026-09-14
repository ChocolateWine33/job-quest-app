from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from core.config import supabase  # Import the client created above


def save_file(cv_file: UploadFile, file_bytes: bytes, unique_filename: str) -> str:
   # Validate MIME type
    if cv_file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )
    # Upload raw bytes directly to Supabase Storage
    try:
        supabase.storage.from_("resumes").upload(
            path=unique_filename,
            file=file_bytes,
            file_options={"content-type": "application/pdf"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to storage: {str(e)}"
        )
