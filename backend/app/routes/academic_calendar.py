from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import engine


router = APIRouter()


@router.get("/academic-calendar")
def get_academic_calendar():

    query = """
        SELECT
            source_title,
            content,
            source_url
        FROM documents
        WHERE source_title ILIKE '%ACADEMIC CALENDAR%'
        ORDER BY id DESC
    """


    with engine.connect() as conn:

        result = conn.execute(text(query))

        calendars = []

        for row in result:

            calendars.append({

                "title": row.source_title,
                "content": row.content,
                "url": row.source_url

            })


    return calendars