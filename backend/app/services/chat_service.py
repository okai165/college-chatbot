from sqlalchemy import text
from app.db.database import engine
from app.rag.retriever import retrieve_similar_chunks
from app.services.llm import client
from sqlalchemy import text
import time


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
            """),
            {
                "query": f"%{query}%"
            }
        )

        rows = result.fetchall()

    return rows


# =========================
# MAIN RAG FUNCTION
# =========================
def generate_response(user_query, session_id):

    # =========================
    # RETRIEVE DOCUMENTS
    # =========================
    docs = retrieve_similar_chunks(user_query)

    print("\n========== RETRIEVED DOCS ==========")
    print(docs)

    # =========================
    # SEARCH FACULTY TABLE
    # =========================
    clean_query = user_query.lower()

    keywords = [
        "who teaches",
        "teacher of",
        "faculty of",
        "timing of",
        "time of",
        "where is",
        "classroom of",
        "room of",
        "class of"
    ]

    for word in keywords:
        clean_query = clean_query.replace(word, "")

    clean_query = clean_query.strip()

    faculty_rows = search_faculty(clean_query)

    faculty_context = ""

    if faculty_rows:

        for row in faculty_rows:

            faculty_context += f"""
Faculty Name: {row.faculty_name}
Subject: {row.subject_name}
Time Slot: {row.time_slot}
Room Number: {row.room_number}

"""

    print("\n========== FACULTY CONTEXT ==========")
    print(faculty_context)

    # =========================
    # BUILD DOCUMENT CONTEXT
    # =========================
    context_chunks = []

    for row in docs:

        if row.content:

            cleaned = row.content.strip()

            if cleaned:
                context_chunks.append(cleaned)

    document_context = "\n\n".join(context_chunks)

    # =========================
    # FINAL CONTEXT
    # =========================
    context = faculty_context + "\n\n" + document_context

    print("\n========== FINAL CONTEXT ==========")
    print(context[:1500])

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

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            print("\n========== GEMINI RESPONSE ==========\n")
            print(response.text)

            return response.text

        except Exception as e:

            print(f"\n❌ RETRY {attempt + 1}/3")
            print(e)

            time.sleep(2)

    return (
        "AI service is temporarily busy. "
        "Please try again in a few seconds."
    )