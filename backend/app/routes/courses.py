from fastapi import APIRouter
from sqlalchemy import text
import re

from app.db.database import engine


router = APIRouter()


@router.get("/available-courses")
def get_available_courses():

    query = """
        SELECT content
        FROM documents
        WHERE content ILIKE '%Programme%'
        AND content ILIKE '%Eligibility%'
        LIMIT 1
    """


    with engine.connect() as conn:

        result = conn.execute(text(query)).fetchone()


    if not result:
        return []


    content = result[0]


    courses = []


    pattern = re.compile(
        r"(\d+)\s+([A-Z][A-Z\s&-]+?)\s+(Major/Minor)\s+\(10\+2\)\s+(.*?)(?=\s+\d+\s+[A-Z])",
        re.S
    )


    matches = pattern.findall(content)


    for match in matches:

        courses.append({

            "sno": match[0],
            "name": match[1].strip(),
            "type": match[2],
            "eligibility": match[3].strip()

        })


    return courses