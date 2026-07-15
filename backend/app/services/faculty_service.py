import re
from sqlalchemy import text

from app.db.database import engine
from app.rag.subject_aliases import SUBJECT_ALIASES


# session memory for faculty
last_subject_by_session = {}


def normalize_subject(subject):

    if not subject:
        return ""


    subject = subject.lower().strip()


    # remove extra spaces
    subject = " ".join(
        subject.split()
    )


    return SUBJECT_ALIASES.get(
        subject,
        subject
    )

def clean_faculty_query(query):

    query = query.lower()
     # remove semester expressions
    query = re.sub(
        r'\b\d+(?:st|nd|rd|th)?\s*(?:semester|sem)\b',
        '',
        query
    )
    remove_words = [
        "who",
        "teaches",
        "teacher",
        "faculty",
        "what",
        "when",
        "where",
        "is",
        "the",
        "class",
        "room",
        "time",
        "schedule",
        "of"
    ]

    for word in remove_words:
        query = re.sub(
            rf"\b{word}\b",
            " ",
            query
        )

    query = re.sub(
        r"[^\w\s]",
        "",
        query
    )

    return " ".join(query.split()).strip()
def extract_semester(query):

    query = query.lower()

    patterns = [
        r'(\d+)(?:st|nd|rd|th)?\s*semester',
        r'semester\s*(\d+)',
        r'sem\s*(\d+)',
        r'(\d+)\s*sem',
        r'(\d+)\s*(?:st|nd|rd|th)?\s*sem'
    ]

    for pattern in patterns:

        match = re.search(pattern, query)

        if match:
            return match.group(1)

    return None

def search_faculty(query, semester=None):

    print("\nSEARCHING FACULTY:", query)
    print("SEMESTER:", semester)

    query = normalize_subject(query)

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    faculty_name,
                    subject_name,
                    time_slot,
                    room_number,
                    semester
                FROM faculty_schedule
                WHERE
                (
                    TRIM(subject_name) ILIKE :q
                    OR TRIM(faculty_name) ILIKE :q
                )
                AND
                (
                    :semester IS NULL
                    OR regexp_replace(semester, '[^0-9]', '', 'g') = :semester
                )
                ORDER BY
                    semester,
                    faculty_name
            """),
            {
                "q": f"%{query}%",
                "semester": semester
            }
        )

        return result.fetchall()



def handle_faculty_query(
        query,
        intent,
        subject,
        operation,
        session_id
):

    semester = extract_semester(query)
    
    # =========================
    # RESTORE PREVIOUS SUBJECT
    # =========================

    if not subject and session_id in last_subject_by_session:

        memory = last_subject_by_session[session_id]

        subject = normalize_subject(memory["subject"])

        if semester is None:
            semester = memory["semester"]


    followup_words = [
        "where",
        "room",
        "lab",
        "location",
        "when",
        "time",
        "timing",
        "schedule",
        "scheduled",
        "lecture"
    ]


    query_lower = query.lower()

    is_followup = any(
        re.search(rf"\b{re.escape(word)}\b", query_lower)
        for word in followup_words
    )


    if is_followup:

        if session_id in last_subject_by_session:

            memory = last_subject_by_session[session_id]

            search_term = memory["subject"]

            if semester is None:
                semester = memory["semester"]

        else:

            search_term = clean_faculty_query(query)

    else:

        if subject:
            search_term = clean_faculty_query(subject)

        else:
            search_term = clean_faculty_query(query)

    print(
        "BEFORE ALIAS:",
        search_term
    )

    search_term = normalize_subject(search_term)

    print(
        "AFTER ALIAS:",
        search_term
    )


    rows = search_faculty(
        search_term,
        semester
    )


    if not rows:
        return None

    row = rows[0]

    last_subject_by_session[session_id] = {
        "subject": row.subject_name,
        "semester": row.semester
    }
    # --------------------------------------
    # Multiple semesters found
    # --------------------------------------

    if semester is None and len(rows) > 1:

        response = f"I found {len(rows)} classes for {row.subject_name}:\n\n"

        for r in rows:

            response += (
                f"Semester {r.semester}\n"
                f"Faculty : {r.faculty_name}\n"
                f"Time    : {r.time_slot}\n"
                f"Room    : {r.room_number}\n\n"
            )

        return response


    if operation == "teacher":

        return (
            f"{row.subject_name} "
            f"(Semester {row.semester}) "
            f"is taught by {row.faculty_name}."
        )


    if operation == "time":

        return (
            f"{row.subject_name} "
            f"(Semester {row.semester}) "
            f"is scheduled at {row.time_slot}."
        )


    if operation == "room":

        return (
            f"{row.subject_name} "
            f"(Semester {row.semester}) "
            f"is taught in {row.room_number}."
        )


    if operation == "schedule":

        return (
            f"{row.subject_name} "
            f"(Semester {row.semester}) "
            f"is taught by {row.faculty_name} "
            f"in {row.room_number} "
            f"at {row.time_slot}."
        )


    return (
        f"{row.subject_name} "
        f"(Semester {row.semester}) "
        f"is taught by {row.faculty_name}."
    )