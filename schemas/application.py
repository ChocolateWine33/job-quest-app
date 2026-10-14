from datetime import date
from pydantic import BaseModel, ConfigDict
from enum import Enum

class JobApplication (BaseModel):
    company_name: str
    role: str

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    apply_date: date
    role_name: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    OFFER = "Offer"

class ApplicationStatusUpdate(BaseModel):
    status = ApplicationStatus

