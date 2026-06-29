from app.tools.patient_tools import (
    validate_patient,
    search_patient,
    register_patient,
    update_patient,
)

from app.tools.appointment_tools import (
    find_appointments,
    schedule_appointment,
    list_patient_appointments,
    cancel_appointment,
)

from app.tools.notification_tools import send_confirmation


def build_tool_registry():
    return {
        "validate_patient": validate_patient,
        "search_patient": search_patient,
        "register_patient": register_patient,
        "update_patient": update_patient,
        "find_appointments": find_appointments,
        "schedule_appointment": schedule_appointment,
        "list_patient_appointments": list_patient_appointments,
        "cancel_appointment": cancel_appointment,
        "send_confirmation": send_confirmation,
    }
