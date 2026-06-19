from sqlalchemy import text
from app.db.database import engine


def notification_exists(source_url):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT 1
                FROM notifications
                WHERE source_url = :source_url
                LIMIT 1
            """),
            {
                "source_url": source_url
            }
        )

        return result.fetchone() is not None


def save_notification(data):

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO notifications
                (
                    title,
                    category,
                    summary,
                    start_date,
                    last_date,
                    eligibility,
                    required_documents,
                    source_url
                )
                VALUES
                (
                    :title,
                    :category,
                    :summary,
                    :start_date,
                    :last_date,
                    :eligibility,
                    :required_documents,
                    :source_url
                )
                ON CONFLICT(source_url)
                DO NOTHING
            """),
            data
        )