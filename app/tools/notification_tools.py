from app.schemas.notification_schema import SendConfirmationRequest


def send_confirmation(**kwargs):
    request = SendConfirmationRequest(**kwargs)

    return {
        "sent": True,
        "patient_id": request.patient_id,
        "appointment_id": request.appointment_id,
        "channel": "email" if request.email else "sms" if request.phone else "none",
        "message": request.message or "Your appointment has been confirmed."
    }