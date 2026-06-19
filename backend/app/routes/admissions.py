from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import engine

router = APIRouter(
    prefix="/admissions",
    tags=["Admissions"]
)


@router.get("/")
def get_admissions():

    with engine.begin() as conn:

        result = conn.execute(
            text("""
                SELECT *
                FROM notifications
                ORDER BY created_at DESC
            """)
        )

        return [
            dict(row._mapping)
            for row in result
        ]