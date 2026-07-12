from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import engine


router = APIRouter()


@router.get("/fee-structure")
def get_fee_structure():

    query = """
        SELECT 
            source_title,
            content
        FROM documents
        WHERE doc_type = 'fee'
        ORDER BY id DESC
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))

        fees = []

        for row in result:
            fees.append({
                "title": row.source_title,
                "content": row.content
            })

    return fees