from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import engine

router = APIRouter(
    prefix="/eligibility",
    tags=["Eligibility"]
)


@router.get("/")
def get_eligibility():

    with engine.begin() as conn:

        result = conn.execute(text("""

            SELECT
                id,
                source_title AS title,
                content AS summary,
                source_url AS pdf_url,
                issued_date AS published_date

            FROM documents

            WHERE doc_type = 'eligibility'

            ORDER BY id DESC

        """))

        return [
            dict(row._mapping)
            for row in result
        ]