from sqlalchemy import text
from app.db.database import engine


def save_notice(
    title,
    pdf_url,
    content
):

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO notices
                (
                    title,
                    notice_type,
                    file_name,
                    file_path,
                    pdf_url
                )
                VALUES
                (
                    :title,
                    :notice_type,
                    :file_name,
                    :file_path,
                    :pdf_url
                )
                ON CONFLICT(pdf_url)
                DO NOTHING
            """),
            {
                "title": title,
                "notice_type": "general",
                "file_name": title,
                "file_path": pdf_url,
                "pdf_url": pdf_url
            }
        )