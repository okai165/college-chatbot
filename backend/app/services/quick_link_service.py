import re
from sqlalchemy import text
from app.db.database import engine


# =====================================================
# Save Quick Link
# Used by the crawler
# =====================================================

def save_quick_link(
    title: str,
    url: str,
    keywords: list[str],
    description: str = ""
):
    """
    Inserts a quick link if it doesn't already exist.
    """

    with engine.begin() as conn:

        existing = conn.execute(
            text("""
                SELECT id
                FROM quick_links
                WHERE url = :url
            """),
            {"url": url},
        ).fetchone()

        if existing:
            return existing.id

        result = conn.execute(
            text("""
                INSERT INTO quick_links
                (
                    title,
                    url,
                    keywords,
                    description
                )
                VALUES
                (
                    :title,
                    :url,
                    :keywords,
                    :description
                )
                RETURNING id
            """),
            {
                "title": title,
                "url": url,
                "keywords": keywords,
                "description": description,
            },
        )

        return result.scalar()


# =====================================================
# Search Quick Link
# Used by chatbot
# =====================================================

def search_quick_link(query: str):
    """
    Returns the best matching quick link.

    Example queries:

    student login
    login portal
    timetable
    know your timetable
    roll number
    know your roll no
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
        # Title
        # -------------------------
        if row.title:

            title = row.title.lower().strip()

            if re.search(r"\b" + re.escape(title) + r"\b", query):
                score = max(score, len(title))

        # -------------------------
        # Keywords
        # -------------------------
        for keyword in (row.keywords or []):

            keyword = keyword.lower().strip()

            if re.search(r"\b" + re.escape(keyword) + r"\b", query):
                score = max(score, len(keyword))

        if score > best_score:
            best_score = score
            best_match = row

    return best_match