from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

class JobApplication (BaseModel):
    company_name: str
    role: str
    job_description: str | None = Field(default=None, min_length=300, max_length=10000)

class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    OFFER = "Offer"

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus | None = None
    job_description: str | None = Field(default=None, min_length=300, max_length=10000)

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    apply_date: date
    role_name: str
    status: ApplicationStatus
    job_description: str | None = None
    
    model_config = ConfigDict(from_attributes=True)




