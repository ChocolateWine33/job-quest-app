from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.user import User
from core.db_setup import get_db
from core.security import get_current_user
from pydantic import BaseModel
from google import genai
from db_ops.retrieval import get_cv_text_by_user, CvNotFoundedError

router = APIRouter(tags=["AI Assistant"])

class Message (BaseModel):
    content: str

client = genai.Client()    

@router.post("/ask")
def send_chat_route(message: Message,
                    db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    try:
        cv_text = get_cv_text_by_user(db=db, user_id=user.id)
    except CvNotFoundedError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    

    contents = []


#     response = client.models.generate_content(
#     model="gemini-3.6-flash",
#     contents=final_prompt,
#     config=types.GenerateContentConfig(
#         system_instruction="You answer only using the provided context." \
#         "If the answer isn't in the context, say you don't know — do not use outside knowledge."
#     )
# )