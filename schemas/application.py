from datetime import date
from pydantic import BaseModel, ConfigDict


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
