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
        "schedule"
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



def search_faculty(query):

    print("\nSEARCHING FACULTY:", query)

    query = query.lower().strip()


    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    faculty_name,
                    subject_name,
                    time_slot,
                    room_number,
                FROM faculty_schedule
                WHERE
                    LOWER(TRIM(subject_name)) LIKE :q
                    OR LOWER(TRIM(faculty_name)) LIKE :q
                ORDER BY
                    CASE
                        WHEN LOWER(TRIM(subject_name)) = :exact
                        THEN 0
                        ELSE 1
                    END
                LIMIT 5
            """),
            {
                "q": f"%{query}%",
                "exact": query
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
    # =========================
    # RESTORE PREVIOUS SUBJECT
    # =========================

    if not subject and session_id in last_subject_by_session:
        subject = normalize_subject(
            last_subject_by_session[session_id]
        )


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


    is_followup = any(
        w in query.lower()
        for w in followup_words
    )


    if is_followup:

        if session_id in last_subject_by_session:
            search_term = last_subject_by_session[session_id]

        else:
            search_term = clean_faculty_query(query)

    else:

        if subject:
            search_term = normalize_subject(subject)

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

    rows = search_faculty(search_term)


    if not rows:
        return None



    row = rows[0]


    # store memory
    last_subject_by_session[session_id] = (
        row.subject_name.lower()
    )


    if operation == "teacher":

        return (
            f"{row.subject_name} is taught by "
            f"{row.faculty_name}."
        )


    if operation == "time":

        return (
            f"{row.subject_name} is scheduled at "
            f"{row.time_slot}."
        )


    if operation == "room":

        return (
            f"{row.subject_name} is taught in "
            f"{row.room_number}."
        )
    if operation == "schedule":

        return (
            f"{row.subject_name} is taught by "
            f"{row.faculty_name} in {row.room_number} "
            f"at {row.time_slot}."
        )


    return (
        f"{row.subject_name} is taught by "
        f"{row.faculty_name}."
    )