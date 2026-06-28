from pydantic import BaseModel


class SendConfirmationRequest(BaseModel):
    patient_id: str = ""
    appointment_id: str = ""
    email: str = ""
    phone: str = ""
    message: str = ""