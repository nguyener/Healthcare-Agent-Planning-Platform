from datetime import datetime, timedelta

from app.schemas.appointment_schema import (
    FindAppointmentsRequest,
    ScheduleAppointmentRequest,
    CancelAppointmentRequest,
)

APPOINTMENTS = []


def find_appointments(**kwargs):
    request = FindAppointmentsRequest(**kwargs)

    today = datetime.today()
    slots = []

    for i in range(1, request.days_ahead + 1):
        day = today + timedelta(days=i)

        slots.append({
            "slot_id": f"SLOT-{i}-1",
            "provider": "Dr. Smith",
            "specialty": request.specialty,
            "start_time": day.replace(
                hour=17,
                minute=30,
                second=0,
                microsecond=0
            ).isoformat(),
            "location": "Seattle Clinic"
        })

        slots.append({
            "slot_id": f"SLOT-{i}-2",
            "provider": "Dr. Lee",
            "specialty": request.specialty,
            "start_time": day.replace(
                hour=18,
                minute=0,
                second=0,
                microsecond=0
            ).isoformat(),
            "location": "Bellevue Clinic"
        })

    return {
        "available": len(slots) > 0,
        "slots": slots
    }


def schedule_appointment(**kwargs):
    request = ScheduleAppointmentRequest(**kwargs)

    appointment = {
        "appointment_id": f"APT-{len(APPOINTMENTS) + 1:05d}",
        "patient_id": request.patient_id,
        "slot_id": request.slot_id,
        "reason": request.reason,
        "status": "scheduled"
    }

    APPOINTMENTS.append(appointment)

    return {
        "scheduled": True,
        "appointment": appointment
    }


def cancel_appointment(**kwargs):
    request = CancelAppointmentRequest(**kwargs)

    for appointment in APPOINTMENTS:
        if appointment["appointment_id"] == request.appointment_id:
            appointment["status"] = "cancelled"

            return {
                "cancelled": True,
                "appointment": appointment
            }

    raise ValueError(f"Appointment not found: {request.appointment_id}")