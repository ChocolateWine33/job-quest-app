from sqlalchemy.orm import Session
from models.user import User

class UserAlreadyExistsError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists!")

class UserNotFoundError(Exception):
    def __init__(self, email: str | None = None, id: int | None = None):
        self.email = email
        self.id = id
        if email:
            message = f"User with email '{email}' was not found."
        elif id is not None:
            message = f"User with ID '{id}' was not found."
        else:
            message = "User was not found."

        super().__init__(message)



def create_user(db: Session, email: str, hashed_password: str ) -> User:

    existing_user = db.query(User).filter_by(email=email).one_or_none()
    if existing_user:
        raise UserAlreadyExistsError(email)

    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user(db: Session, email: str) -> User:

    user = db.query(User).filter_by(email=email).one_or_none()
    if user is None:
        raise UserNotFoundError(email=email)
    return user

