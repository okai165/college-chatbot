from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import engine

router = APIRouter()


# =========================
# GET ALL FACULTY
# =========================
@router.get("/faculty")
def get_faculty():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT *
                FROM faculty_schedule
                ORDER BY id DESC
            """)
        )

        rows = result.fetchall()

    faculty = []

    for row in rows:
        faculty.append({
            "id": row.id,
            "faculty_name": row.faculty_name,
            "subject_name": row.subject_name,
            "time_slot": row.time_slot,
            "room_number": row.room_number
        })

    return faculty


# =========================
# ADD FACULTY
# =========================
@router.post("/faculty")
def add_faculty(data: dict):

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO faculty_schedule
                (
                    faculty_name,
                    subject_name,
                    time_slot,
                    room_number
                )
                VALUES
                (
                    :faculty_name,
                    :subject_name,
                    :time_slot,
                    :room_number
                )
            """),
            {
                "faculty_name": data["faculty_name"],
                "subject_name": data["subject_name"],
                "time_slot": data["time_slot"],
                "room_number": data["room_number"]
            }
        )

    return {
        "message": "Faculty added successfully"
    }


# =========================
# DELETE FACULTY
# =========================
@router.delete("/faculty/{faculty_id}")
def delete_faculty(faculty_id: int):

    with engine.begin() as conn:

        conn.execute(
            text("""
                DELETE FROM faculty_schedule
                WHERE id = :id
            """),
            {
                "id": faculty_id
            }
        )

    return {
        "message": "Faculty deleted successfully"
    }
# =========================
# UPDATE FACULTY
# =========================
@router.put("/faculty/{faculty_id}")
def update_faculty(faculty_id: int, data: dict):

    with engine.begin() as conn:

        conn.execute(
            text("""
                UPDATE faculty_schedule
                SET
                    faculty_name = :faculty_name,
                    subject_name = :subject_name,
                    time_slot = :time_slot,
                    room_number = :room_number
                WHERE id = :id
            """),
            {
                "id": faculty_id,
                "faculty_name": data["faculty_name"],
                "subject_name": data["subject_name"],
                "time_slot": data["time_slot"],
                "room_number": data.get("room_number")
            }
        )

    return {
        "message": "Faculty updated successfully"
    }