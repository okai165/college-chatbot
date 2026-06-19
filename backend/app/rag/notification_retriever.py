from sqlalchemy import text
from app.db.database import engine


def search_notifications():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    title,
                    summary,
                    eligibility,
                    start_date,
                    last_date
                FROM notifications
                ORDER BY id DESC
                LIMIT 20
            """)
        )

        return result.fetchall()