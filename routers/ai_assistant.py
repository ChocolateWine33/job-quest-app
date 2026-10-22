from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.user import User
from core.db_setup import get_db
from core.security import get_current_user
from pydantic import BaseModel
from google import genai
from google.genai import types
from db_ops.retrieval_save import get_cv_text_by_user, get_messages_by_user, save_message ,CvNotFoundError
from services.ai_service import get_contents, get_ai_response, AiResponseError

router = APIRouter(tags=["AI Assistant"])

class Message (BaseModel):
    content: str


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

    try:
        response = get_ai_response(contents=contents, cv_text=cv_text)
    except AiResponseError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The assistant couldn't generate a reply, please try again!"
        )

    #What happens if one message got saved and the other one is not? Check Later
    save_message(db=db, role="user", user_id=user.id, content=message.content)
    save_message(db=db, role="model", user_id=user.id, content=response)

    return {
        "AI_assistant": response
    }

@router.post("/application_analysis/{application_id}", status_code=status.HTTP_201_CREATED)
def add_application_route(application_id: int,
                           db: Session = Depends(get_db),
                           user: User = Depends(get_current_user)):


    pass
