from sqlalchemy import text
from app.db.database import engine


def save_scholarship(
    title,
    pdf_url,
    details
):

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO scholarships
                (
                    title,
                    pdf_url,
                    details
                )
                VALUES
                (
                    :title,
                    :pdf_url,
                    :details
                )
                ON CONFLICT(pdf_url)
                DO NOTHING
            """),
            {
                "title": title,
                "pdf_url": pdf_url,
                "details": details
            }
        )