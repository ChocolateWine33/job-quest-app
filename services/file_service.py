from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from core.config import supabase  # Import the client created above
import uuid
import io
import httpx
from pypdf import PdfReader

# TODO: verify supabase client blocking behavior
def save_file(cv_file: UploadFile, user_id: int) -> str:
   # Validate MIME type
    if cv_file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )

    file_bytes = cv_file.file.read()

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

def extract_text_from_url(cv_url: str) -> str:
    # 1. Download the PDF file bytes from the Supabase URL
    try:
        response = httpx.get(cv_url)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException (
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to download CV text From the url: {e}"
        )
    # 2. Load the bytes into an in-memory stream
    pdf_file_in_memory = io.BytesIO(response.content)

    # 3. Read and extract text page by page
    reader = PdfReader(pdf_file_in_memory)
    cv_text = "".join(page.extract_text() for page in reader.pages).strip()
    if not cv_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a CV that contains text."
        )
    return cv_text
