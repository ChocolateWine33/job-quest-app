from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
from core.config import settings
from core.db_setup import get_db
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from models.user import User
from db_ops.user import get_user
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

def create_access_token(data: dict) -> str:
    data_to_be_encoded = data.copy()
    token_expiry_date = datetime.now(timezone.utc) + timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_be_encoded.update({"exp": token_expiry_date})
    encoded_jwt = jwt.encode(data_to_be_encoded, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt

# what does this line do how to think about it  
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Why do I make Depends get db here but when creating in db_obs I don't
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    pass
    # current_user = get_user() 