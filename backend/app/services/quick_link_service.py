import re
from sqlalchemy import text
from app.db.database import engine


def search_quick_link(query: str):
    """
    Search for the best matching quick link.

    Examples:
    - student login
    - login portal
    - know your timetable
    - timetable
    - time table
    - know your roll no
    - roll number
    """

    query = query.lower().strip()

    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    id,
                    title,
                    keywords,
                    url,
                    description
                FROM quick_links
            """)
        ).fetchall()

    best_match = None
    best_score = 0

    for row in rows:

        score = 0

        # -------------------------
        # Match title
        # -------------------------
        if row.title:
            title = row.title.lower().strip()

            pattern = r"\b" + re.escape(title) + r"\b"

            if re.search(pattern, query):
                score = max(score, len(title))

        # -------------------------
        # Match keywords
        # -------------------------
        for keyword in (row.keywords or []):

            keyword = keyword.lower().strip()

            pattern = r"\b" + re.escape(keyword) + r"\b"

            if re.search(pattern, query):
                score = max(score, len(keyword))

        # -------------------------
        # Keep best match
        # -------------------------
        if score > best_score:
            best_score = score
            best_match = row

    return best_match