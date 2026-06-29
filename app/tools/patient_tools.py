from datetime import datetime

from app.schemas.patient_schema import (
    ValidatePatientRequest,
    SearchPatientRequest,
    RegisterPatientRequest,
    UpdatePatientRequest,
)
from app.database import get_connection, init_db, next_external_id, row_to_dict

init_db()


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

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT patient_id, full_name, dob, phone, email, state
            FROM patients
            WHERE lower(full_name) = lower(?) AND dob = ?
            """,
            (request.full_name, request.dob),
        ).fetchone()

    patient = row_to_dict(row)

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

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT patient_id, full_name, dob, phone, email, state
            FROM patients
            WHERE lower(full_name) = lower(?) AND dob = ?
            """,
            (request.full_name, request.dob),
        ).fetchone()

        if existing is not None:
            return {
                "created": False,
                "patient": row_to_dict(existing),
                "message": "Patient already exists"
            }

        patient_id = next_external_id(connection, "patients", "PAT")
        connection.execute(
            """
            INSERT INTO patients (patient_id, full_name, dob, phone, email, state)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                request.full_name,
                request.dob,
                request.phone,
                request.email,
                request.state,
            ),
        )

        row = connection.execute(
            """
            SELECT patient_id, full_name, dob, phone, email, state
            FROM patients
            WHERE patient_id = ?
            """,
            (patient_id,),
        ).fetchone()

    return {
        "created": True,
        "patient": row_to_dict(row)
    }


def update_patient(**kwargs):
    request = UpdatePatientRequest(**kwargs)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT patient_id, full_name, dob, phone, email, state
            FROM patients
            WHERE patient_id = ?
            """,
            (request.patient_id,),
        ).fetchone()

        if row is None:
            raise ValueError(f"Patient not found: {request.patient_id}")

        patient = row_to_dict(row)
        phone = request.phone if request.phone is not None else patient["phone"]
        email = request.email if request.email is not None else patient["email"]
        state = request.state if request.state is not None else patient["state"]

        connection.execute(
            """
            UPDATE patients
            SET phone = ?, email = ?, state = ?, updated_at = CURRENT_TIMESTAMP
            WHERE patient_id = ?
            """,
            (phone, email, state, request.patient_id),
        )

        updated = connection.execute(
            """
            SELECT patient_id, full_name, dob, phone, email, state
            FROM patients
            WHERE patient_id = ?
            """,
            (request.patient_id,),
        ).fetchone()

    return {
        "updated": True,
        "patient": row_to_dict(updated)
    }
