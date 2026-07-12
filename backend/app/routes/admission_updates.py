from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import engine

router = APIRouter()


@router.get("/admission-updates")
def get_admission_updates():

    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT
                id,
                title,
                summary,
                pdf_url,
                published_date
            FROM admission_updates
            ORDER BY published_date DESC
        """))

        updates = []

        for row in result:

            updates.append({

                "id": row.id,
                "title": row.title,
                "summary": row.summary,
                "pdf_url": row.pdf_url,
                "published_date": row.published_date

            })

        return updates