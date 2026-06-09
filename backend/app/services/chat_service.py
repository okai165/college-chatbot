from sqlalchemy import text
from app.db.database import engine
from app.rag.retriever import retrieve_similar_chunks
from app.services.llm import client
from sqlalchemy import text
import time

# Store last faculty subject per session
last_subject_by_session = {}
# =========================
# CHAT MEMORY
# =========================
def get_chat_history(session_id, limit=3):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT role, message
                FROM chat_history
                WHERE session_id = :session_id
                ORDER BY id DESC
                LIMIT :limit
            """),
            {
                "session_id": session_id,
                "limit": limit
            }
        )

        rows = result.fetchall()

    return rows[::-1]


# =========================
# FACULTY SEARCH
# =========================
def search_faculty(query):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    faculty_name,
                    subject_name,
                    time_slot,
                    room_number
                FROM faculty_schedule
                WHERE
                    LOWER(subject_name) LIKE LOWER(:query)
                    OR LOWER(faculty_name) LIKE LOWER(:query)
                ORDER BY
                    CASE
                        WHEN LOWER(subject_name) = LOWER(:exact_query) THEN 1
                        WHEN LOWER(subject_name) LIKE LOWER(:query) THEN 2
                        WHEN LOWER(faculty_name) LIKE LOWER(:query) THEN 3
                        ELSE 4
                    END
                LIMIT 5
            """),
            {
                "query": f"%{query}%",
                "exact_query": query
            }
        )

        rows = result.fetchall()

    return rows


# =========================
# MAIN RAG FUNCTION
# =========================
def generate_response(user_query, session_id):
    query = user_query.lower().strip()

    # Greetings
    if query in ["hi", "hello", "hey"]:
        return (
            "Hello! 👋 Welcome to the College Information Assistant. "
            "How can I help you today?"
        )

    if query == "how are you":
        return "I'm doing well. How can I assist you today?"

    if query in ["thanks", "thank you"]:
        return "You're welcome! 😊"

    if query in ["bye", "goodbye"]:
        return "Goodbye! Have a great day."
    # =========================
    # RETRIEVE DOCUMENTS
    # =========================
    docs = retrieve_similar_chunks(user_query)

    # print("\n========== RETRIEVED DOCS ==========")
    print(docs)

    # =========================
    # SEARCH FACULTY TABLE
    # =========================
    import re

    clean_query = user_query.lower()

    remove_words = [
        "who",
        "teaches",
        "teach",
        "teacher",
        "faculty",
        "of",
        "what",
        "when",
        "where",
        "is",
        "the",
        "class",
        "room",
        "classroom",
        "timing",
        "time",
        "schedule",
        "for",
        "at",
        "in"
    ]

    for word in remove_words:

        clean_query = re.sub(
            rf"\b{word}\b",
            " ",
            clean_query
        )
    clean_query = " ".join(clean_query.split())

    # Handle follow-up questions
    history = get_chat_history(session_id)

    followup_words = [
        "where",
        "when",
        "time",
        "timing",
        "at what time",
        "room",
        "classroom"
    ]

    if (
        query in followup_words
        and session_id in last_subject_by_session
    ):
        clean_query = last_subject_by_session[session_id]
    
    print("USER QUERY:", user_query)
    print("CLEAN QUERY:", clean_query)
    print("LAST SUBJECT:", last_subject_by_session.get(session_id))
    # Search faculty
    faculty_rows = search_faculty(clean_query) if clean_query.strip() else []

    # Always define row
    row = faculty_rows[0] if faculty_rows else None

    faculty_context = ""

    if row:
        last_subject_by_session[session_id] = row.subject_name.lower()

        if (
            "who teaches" in query
            or "teacher" in query
            or "faculty" in query
        ):

            return (
                f"{row.subject_name} is taught by "
                f"{row.faculty_name}."
            )

        elif (
            "time" in query
            or "when" in query
            or "timing" in query
            or "at what time" in query
        ):

            return (
                f"{row.subject_name} class is "
                f"scheduled from {row.time_slot}."
            )

        elif (
            "room" in query
            or "where" in query
            or "classroom" in query
        ):

            return (
                f"{row.subject_name} class is "
                f"held in room {row.room_number}."
            )

        else:

            return f"""
    Faculty Name: {row.faculty_name}
    Subject: {row.subject_name}
    Time Slot: {row.time_slot}
    Room Number: {row.room_number}
    """
    

    # print("\n========== FACULTY CONTEXT ==========")
    # print(faculty_context)

    # =========================
    # BUILD DOCUMENT CONTEXT
    # =========================
    context_chunks = []

    for row in docs:

        if row.content:

            cleaned = row.content.strip()

            if cleaned:
                context_chunks.append(cleaned)
    
    print("\n========== ALL CHUNKS ==========")

    for i, chunk in enumerate(context_chunks):
        print(f"\nCHUNK {i+1}")
        print(chunk[:1000])
    document_context = "\n\n".join(context_chunks)
    
    # =========================
    # FINAL CONTEXT
    # =========================
    context = faculty_context + "\n\n" + document_context
    # simple_keywords = [
    #     "syllabus",
    #     "faculty",
    #     "teacher",
    #     "teachers",
    #     "exam",
    #     "examination",
    #     "admission",
    #     "notice",
    #     "result",
    #     "timetable",
    #     "schedule"
    # ]

    # if any(word in query for word in simple_keywords):

    #     if context.strip():
    #         return context

    # print("\n========== FINAL CONTEXT ==========")
    # print(context[:1500])

    # =========================
    # STRICT GUARD
    # =========================
    if (
        len(context_chunks) == 0
        and len(faculty_rows) == 0
    ):

        return (
            "Sorry, I cannot find relevant information "
            "in the college documents."
        )
    # =========================
    # DIRECT RESPONSE
    # =========================
    # if len(context) < 3000 and context.strip():

    #     return context
    # =========================
    # CHAT MEMORY
    # =========================
    history = get_chat_history(session_id)
    

    memory_text = "\n".join(
        [f"{h.role}: {h.message}" for h in history]
    ) if history else ""

    # =========================
    # STRICT PROMPT
    # =========================
    prompt = f"""
You are a strict college assistant chatbot.

RULES:
- Answer ONLY from the provided CONTEXT
- Never use outside knowledge
- If answer is not present in context, say exactly:
  "Sorry, I cannot find relevant information in the college documents."
- Keep responses short and factual

CHAT HISTORY:
{memory_text}

CONTEXT:
{context}

USER QUESTION:
{user_query}
"""

    print("\n========== SENDING TO GEMINI ==========\n")

    # =========================
    # GEMINI RESPONSE WITH RETRY
    # =========================
    for attempt in range(3):

        try:
            print("Gemini API call started")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            print("\n========== GEMINI RESPONSE ==========\n")
            print(response.text)

            return response.text

        except Exception as e:

            print(f"\n❌ RETRY {attempt + 1}/3")
            import traceback
            traceback.print_exc()

            time.sleep(2)

    return (
        "AI service is temporarily busy. "
        "Please try again in a few seconds."
    )