import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserReg(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        # Rule 1: Minimum Length
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Rule 2: Must contain at least one uppercase letter
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        # Rule 3: Must contain at least one lowercase letter
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        # Rule 4: Must contain at least one digit
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")

        # Rule 5: Must contain at least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")

        return value 

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy ORM models


class Token(BaseModel):
    access_token: str
    token_type: str