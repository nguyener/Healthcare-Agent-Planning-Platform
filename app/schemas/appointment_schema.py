from pydantic import BaseModel


class FindAppointmentsRequest(BaseModel):
    specialty: str = "primary care"
    days_ahead: int = 7


class ScheduleAppointmentRequest(BaseModel):
    patient_id: str
    slot_id: str
    reason: str = "General appointment"
    provider: str = ""
    specialty: str = ""
    start_time: str = ""
    location: str = ""


class ListPatientAppointmentsRequest(BaseModel):
    patient_id: str
    status: str | None = None


class CancelAppointmentRequest(BaseModel):
    appointment_id: str
