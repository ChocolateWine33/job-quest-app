from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.user import User
from core.db_setup import get_db
from core.security import get_current_user
from db_ops.retrieval_save import get_cv_text_by_user, get_messages_by_user, save_message ,CvNotFoundError
from services.ai_service import get_contents, get_ai_response, get_application_analysis, AiResponseError
from db_ops.application_tracker import get_a_single_user_application, save_application_analysis, ApplicationNotFoundError
from schemas.ai_job_assistant import Message, ApplicationAnalysis


router = APIRouter(tags=["AI Assistant"])


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

@router.post("/application_analysis/{application_id}", response_model=ApplicationAnalysis)
def create_application_analysis_route(application_id: int,
                           db: Session = Depends(get_db),
                           user: User = Depends(get_current_user)):

    try:
        application = get_a_single_user_application(db=db, user_id=user.id, application_id=application_id)
        cv_text = get_cv_text_by_user(db=db, user_id=user.id)
    except (CvNotFoundError, ApplicationNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The Application or the Cv Might be missing :'( " 
        )

    if not application.job_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please add a job description to that application!"
        ) 
    
    analysis = get_application_analysis(cv_text=cv_text, job_description=application.job_description)
    save_application_analysis(db=db, application=application, analysis=analysis)
    return analysis
   