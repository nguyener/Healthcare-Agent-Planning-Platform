from datetime import datetime, timedelta

from app.schemas.appointment_schema import (
    FindAppointmentsRequest,
    ScheduleAppointmentRequest,
    ListPatientAppointmentsRequest,
    CancelAppointmentRequest,
)
from app.database import get_connection, init_db, next_external_id, row_to_dict

init_db()


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

    with get_connection() as connection:
        appointment_id = next_external_id(
            connection,
            "appointments",
            "APT",
        )
        connection.execute(
            """
            INSERT INTO appointments (
                appointment_id,
                patient_id,
                slot_id,
                provider,
                specialty,
                start_time,
                location,
                reason,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                appointment_id,
                request.patient_id,
                request.slot_id,
                request.provider,
                request.specialty,
                request.start_time,
                request.location,
                request.reason,
                "scheduled",
            ),
        )
        row = connection.execute(
            """
            SELECT
                appointment_id,
                patient_id,
                slot_id,
                provider,
                specialty,
                start_time,
                location,
                reason,
                status
            FROM appointments
            WHERE appointment_id = ?
            """,
            (appointment_id,),
        ).fetchone()

    return {
        "scheduled": True,
        "appointment": row_to_dict(row)
    }


def list_patient_appointments(**kwargs):
    request = ListPatientAppointmentsRequest(**kwargs)

    query = """
        SELECT
            appointment_id,
            patient_id,
            slot_id,
            provider,
            specialty,
            start_time,
            location,
            reason,
            status
        FROM appointments
        WHERE patient_id = ?
    """
    params = [request.patient_id]

    if request.status:
        query += " AND status = ?"
        params.append(request.status)

    query += " ORDER BY created_at DESC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    appointments = [row_to_dict(row) for row in rows]

    return {
        "found": len(appointments) > 0,
        "appointments": appointments
    }


def cancel_appointment(**kwargs):
    request = CancelAppointmentRequest(**kwargs)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                appointment_id,
                patient_id,
                slot_id,
                provider,
                specialty,
                start_time,
                location,
                reason,
                status
            FROM appointments
            WHERE appointment_id = ?
            """,
            (request.appointment_id,),
        ).fetchone()

        if row is None:
            raise ValueError(f"Appointment not found: {request.appointment_id}")

        connection.execute(
            """
            UPDATE appointments
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE appointment_id = ?
            """,
            ("cancelled", request.appointment_id),
        )

        updated = connection.execute(
            """
            SELECT
                appointment_id,
                patient_id,
                slot_id,
                provider,
                specialty,
                start_time,
                location,
                reason,
                status
            FROM appointments
            WHERE appointment_id = ?
            """,
            (request.appointment_id,),
        ).fetchone()

    return {
        "cancelled": True,
        "appointment": row_to_dict(updated)
    }
