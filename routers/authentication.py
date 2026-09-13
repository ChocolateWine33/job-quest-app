from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from core.db_setup import get_db
from schemas.user import UserReg, UserResponse, Token
from core.security import hash_password, verify_password, create_access_token
from db_ops.user import create_user, get_user, UserAlreadyExistsError, UserNotFoundError
from fastapi.security import OAuth2PasswordRequestForm


class InvalidCredentialsError(Exception):
    pass

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_route(new_user: UserReg, db: Session = Depends(get_db)):

    new_user.password = hash_password(new_user.password)
    try:
        return create_user(db=db, email=new_user.email, hashed_password=new_user.password)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login_route(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    try:
        account_holder = get_user(db=db, email=form_data.username)
        
        if not verify_password(
            plain_password=form_data.password, 
            hashed_password=account_holder.hashed_password
        ):
            raise InvalidCredentialsError()
    except (UserNotFoundError, InvalidCredentialsError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!")
    
    access_token = create_access_token(data={"sub": account_holder.email})
    return{
        "access_token": access_token,
        "token_type": "bearer"
    }