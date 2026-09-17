from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from core.config import supabase  # Import the client created above
import uuid

# TODO: verify supabase client blocking behavior
async def save_file(cv_file: UploadFile, user_id: int) -> str:
   # Validate MIME type
    if cv_file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )
    
    file_bytes = await cv_file.read()

    # Generate a unique filename (cv_<user_id>_<uuid>.pdf)
    file_extension = cv_file.filename.split(".")[-1]
    unique_filename = f"cv_{user_id}_{uuid.uuid4().hex}.{file_extension}"

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
    # Get the public download URL from Supabase
    cv_public_url = supabase.storage.from_("resumes").get_public_url(unique_filename)
    return cv_public_url

