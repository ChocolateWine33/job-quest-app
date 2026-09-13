from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
from core.config import settings
from core.db_setup import get_db
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from models.user import User
from db_ops.user import get_user, UserNotFoundError
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:


    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials!",
        headers={"WWW-Authenticate": "Bearer"},  # Tells the client: "Use a Bearer Token!"
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        email = payload.get("sub")
# Checking if email is None: is just your backend asking one final question before hitting the database:- 
# "Does this token actually contain the identity claim (sub) required to log someone in?"
        if email is None:
            raise credential_exception
    except JWTError:
        raise credential_exception

    try:
        user = get_user(db=db, email=email)
    except UserNotFoundError:
        raise credential_exception
    return user