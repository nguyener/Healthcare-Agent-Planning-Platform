from pydantic import BaseModel


class ValidatePatientRequest(BaseModel):
    full_name: str
    dob: str
    state: str


class SearchPatientRequest(BaseModel):
    full_name: str
    dob: str


class RegisterPatientRequest(BaseModel):
    full_name: str
    dob: str
    phone: str = ""
    email: str = ""
    state: str = "WA"


class UpdatePatientRequest(BaseModel):
    patient_id: str
    phone: str | None = None
    email: str | None = None
    state: str | None = None