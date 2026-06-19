from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import engine

router = APIRouter(tags=["Notifications"])


@router.get("/notifications")
def get_notifications():

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