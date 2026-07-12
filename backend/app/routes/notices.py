from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import engine

router = APIRouter(
    prefix="/notices",
    tags=["Notices"]
)


@router.get("/latest")
def latest_notices(limit: int = 10):

    query = text("""
        SELECT
            id,
            title,
            notice_type,
            pdf_url,
            created_at

        FROM notices

        ORDER BY created_at DESC

        LIMIT :limit
    """)

    with engine.connect() as conn:

        result = conn.execute(
            query,
            {"limit": limit}
        )

        notices = [

            {
                "id": row.id,
                "title": row.title,
                "type": row.notice_type,
                "pdf_url": row.pdf_url,
                "created_at": row.created_at,
            }

            for row in result

        ]

    return notices