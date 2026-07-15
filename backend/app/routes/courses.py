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
        WHERE document_name = 'AvailableCourses.pdf'
        ORDER BY id
    """


    with engine.connect() as conn:
        rows = conn.execute(text(query)).fetchall()


    if not rows:
        return []


    print("TOTAL CHUNKS:", len(rows))


    # Merge all chunks
    content = " ".join(
        row[0] for row in rows
    )


    # Remove only page footer
    content = re.sub(
        r"Page\s+\d+\s+of\s+\d+",
        " ",
        content
    )


    # Remove college header but keep S No
    content = re.sub(
        r"Govt\. College for Women, M\.A Road Srinagar",
        " ",
        content
    )


    # Remove repeated title only
    content = re.sub(
        r"Eligibility Criteria for Various FYUG \(3\+1\) Honours Programmes – Academic Session 2026-27",
        " ",
        content
    )


    content = " ".join(content.split())


    courses = []


    pattern = re.compile(
        r"(\d+)\s+"
        r"([A-Z][A-Z\s&-]+?)\s+"
        r"(Major/Minor|Minor)\s+"
        r"(.*?)(?=\s+\d+\s+[A-Z]|$)",
        re.S
    )


    matches = pattern.findall(content)


    print("TOTAL MATCHES:", len(matches))


    seen = set()


    for match in matches:

        sno = match[0]

        if sno in seen:
            continue

        seen.add(sno)

        courses.append({

            "sno": sno,

            "name": match[1].strip(),

            "type": match[2],

            "eligibility": " ".join(
                match[3].split()
            )

        })


    return courses