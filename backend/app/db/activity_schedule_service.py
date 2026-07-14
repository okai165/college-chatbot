from sqlalchemy import text
from app.db.database import engine


def save_activity_schedule(
    title,
    date,
    source_url,
    data
):

    if not data:
        return False


    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO activity_schedule
                (
                    title,
                    schedule_data,
                    source_url,
                    created_at
                )
                VALUES
                (
                    :title,
                    :schedule_data,
                    :source_url,
                    NOW()
                )
            """),
            {
                "title": title,
                "schedule_data": str(data),
                "source_url": source_url
            }
        )

    return True