from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.user import User
from core.db_setup import get_db
from core.security import get_current_user
from pydantic import BaseModel
from google import genai
from google.genai import types
from db_ops.retrieval_save import get_cv_text_by_user, get_messages_by_user, save_message ,CvNotFoundError
from services.ai_service import get_contents

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
    except CvNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    chat_history = get_messages_by_user(db=db, user_id=user.id)

    contents = get_contents(chat_history=chat_history, user_message=message.content)

    response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=contents,
    config=types.GenerateContentConfig(
        system_instruction="You answer only using the provided context." \
        "If the answer isn't in the context, say you don't know — do not use outside knowledge."
    )
)

    save_message(db=db, role="user", user_id=user.id, content=message.content)
    save_message(db=db, role="model", user_id=user.id, content=response.text)

    return {
        "AI_assistant": response.text
    }
