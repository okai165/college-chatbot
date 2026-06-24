from sqlalchemy import text
from app.db.database import engine


def keyword_search(query):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    content,
                    document_name,
                    0.0 as distance
                FROM documents
                WHERE
                    document_name ILIKE :q
                    OR content ILIKE :q
                LIMIT 10
            """),
            {
                "q": f"%{query}%"
            }
        )

        return result.fetchall()