from datetime import datetime

from app.schemas.patient_schema import (
    ValidatePatientRequest,
    SearchPatientRequest,
    RegisterPatientRequest,
    UpdatePatientRequest,
)

PATIENTS = {}


def validate_patient(**kwargs):
    request = ValidatePatientRequest(**kwargs)

    if request.state.upper() not in ["WA", "WASHINGTON"]:
        raise ValueError("Only Washington residents are eligible")

    birth_date = datetime.strptime(request.dob, "%m/%d/%Y")
    today = datetime.today()

    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )

    if age < 18:
        raise ValueError("Patient must be at least 18 years old")

    return {
        "valid": True,
        "age": age,
        "state": request.state
    }


def search_patient(**kwargs):
    request = SearchPatientRequest(**kwargs)

    key = f"{request.full_name.lower()}::{request.dob}"
    patient = PATIENTS.get(key)

    return {
        "found": patient is not None,
        "patient": patient
    }


def register_patient(**kwargs):
    request = RegisterPatientRequest(**kwargs)

    validate_patient(
        full_name=request.full_name,
        dob=request.dob,
        state=request.state,
    )

    key = f"{request.full_name.lower()}::{request.dob}"

    if key in PATIENTS:
        return {
            "created": False,
            "patient": PATIENTS[key],
            "message": "Patient already exists"
        }

    patient = {
        "patient_id": f"PAT-{len(PATIENTS) + 1:05d}",
        "full_name": request.full_name,
        "dob": request.dob,
        "phone": request.phone,
        "email": request.email,
        "state": request.state,
    }

    PATIENTS[key] = patient

    return {
        "created": True,
        "patient": patient
    }


def update_patient(**kwargs):
    request = UpdatePatientRequest(**kwargs)

    for patient in PATIENTS.values():
        if patient["patient_id"] == request.patient_id:
            if request.phone is not None:
                patient["phone"] = request.phone
            if request.email is not None:
                patient["email"] = request.email
            if request.state is not None:
                patient["state"] = request.state

            return {
                "updated": True,
                "patient": patient
            }

    raise ValueError(f"Patient not found: {request.patient_id}")