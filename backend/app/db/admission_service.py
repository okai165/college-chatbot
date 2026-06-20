from sqlalchemy import text
from app.db.database import engine


def admission_exists(pdf_url):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT 1
                FROM admission_updates
                WHERE pdf_url = :pdf_url
                LIMIT 1
            """),
            {
                "pdf_url": pdf_url
            }
        )

        return result.fetchone() is not None


def save_admission(
    title,
    date,
    pdf_url,
    summary
):

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO admission_updates
                (
                    title,
                    published_date,
                    pdf_url,
                    summary
                )
                VALUES
                (
                    :title,
                    :published_date,
                    :pdf_url,
                    :summary
                )
                ON CONFLICT(pdf_url)
                DO NOTHING
            """),
            {
                "title": title,
                "published_date": date,
                "pdf_url": pdf_url,
                "summary": summary
            }
        )