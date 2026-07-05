import os
from sqlalchemy import text
from app.db.database import engine
from app.rag.retriever import retrieve_similar_chunks
from app.services.llm import generate_llm_response
from app.rag.notification_retriever import search_notifications
from app.rag.keyword_search import keyword_search
from app.rag.query_analyzer import analyze_query
from app.rag.subject_aliases import SUBJECT_ALIASES
from app.crawler.doc_type_mapper import map_doc_type
import time
import re

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
            {"session_id": session_id, "limit": limit}
        )

        rows = result.fetchall()

    return rows[::-1]


# =========================
# QUERY REWRITER (NOW USING YOUR LLM)
# =========================
def rewrite_query(user_query, history):

    memory_text = "\n".join(
        [f"{h.role}: {h.message}" for h in history]
    ) if history else ""

    prompt = f"""
You are a query rewriting assistant.

Convert follow-up questions into standalone questions.

Conversation:
{memory_text}

User:
{user_query}

Standalone Question:
"""

    try:
        rewritten_query = generate_llm_response(prompt).strip()

        print("\n========== REWRITTEN QUERY ==========")
        print(rewritten_query)

        return rewritten_query

    except Exception:
        return user_query


# =========================
# INTENT CLASSIFIER
# =========================
def classify_intent(query: str) -> str:
    query = query.lower()

    if any(x in query for x in ["can i wear", "allowed", "dress code", "uniform"]):
        return "policy"

    if any(x in query for x in ["who teaches", "faculty", "teacher"]):
        return "faculty"

    if any(x in query for x in ["where", "when", "time", "room"]):
        return "schedule"

    if "examination cell" in query or "exam cell" in query:
        return "examination"

    if "grievance" in query or "complaint" in query:
        return "grievance"

    if "library" in query:
        return "library"

    if "hostel" in query:
        return "hostel"

    if "iqac" in query:
        return "iqac"

    if "nirf" in query:
        return "nirf"

    if "ncc" in query:
        return "ncc"

    if "entrepreneurship" in query:
        return "entrepreneurship"

    if "innovation" in query or "incubation" in query:
        return "innovation"

    return "general"


# =========================
# FACULTY SEARCH
# =========================
def search_faculty(query: str):

    query = query.strip().lower()

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT faculty_name, subject_name, time_slot, room_number
                FROM faculty_schedule
                WHERE
                    LOWER(subject_name) = :query
                    OR LOWER(subject_name) LIKE :like_query
                    OR LOWER(faculty_name) LIKE :like_query
                LIMIT 5
            """),
            {
                "query": query,
                "like_query": f"%{query}%"
            }
        )

        rows = result.fetchall()
        return rows


# =========================
# CLEAN FACULTY QUERY
# =========================
def clean_faculty_query(rewritten_query: str) -> str:
    query = rewritten_query.lower()

    remove_words = [
        "who", "teaches", "teacher", "faculty",
        "what", "when", "where", "is", "the",
        "class", "room", "time", "schedule"
    ]

    for word in remove_words:
        query = re.sub(rf"\b{word}\b", " ", query)

    query = re.sub(r"[^\w\s]", "", query)
    return " ".join(query.split()).strip()


# =========================
# SUBJECT NORMALIZATION
# =========================
def normalize_subject(subject):

    if not subject:
        return ""

    subject = subject.lower().strip()
    return SUBJECT_ALIASES.get(subject, subject)


# =========================
# MAIN RAG FUNCTION
# =========================
def generate_response(user_query, session_id):

    query = user_query.lower().strip()
    notifications = []

    # =========================
    # SMALL TALK
    # =========================
    if query in ["hi", "hello", "hey"]:
        return "Hello! 👋 How can I help you today?"

    if query in ["bye", "goodbye"]:
        return "Goodbye! Have a great day."

    # =========================
    # INTENT
    # =========================
    intent = classify_intent(user_query)

    # =========================
    # CHAT HISTORY
    # =========================
    history = get_chat_history(session_id)

    followup_words = ["where", "when", "room", "time"]

    if any(word in query for word in followup_words):
        rewritten_query = rewrite_query(user_query, history)
    else:
        rewritten_query = user_query

    # =========================
    # ANALYZE QUERY
    # =========================
    analysis = analyze_query(user_query)

    docs = retrieve_similar_chunks(
        rewritten_query + " " + analysis.get("subject", ""),
        semester=analysis.get("semester"),
        exam_type=analysis.get("exam_type"),
        doc_type=analysis.get("intent")
    )

    subject = analysis.get("subject")

    # =========================
    # FACULTY SEARCH QUERY HANDLING
    # =========================
    if subject:
        clean_query = normalize_subject(subject)
    elif session_id in last_subject_by_session:
        # Reuse last subject if analyzer missed it
        clean_query = last_subject_by_session[session_id]
    else:
        clean_query = clean_faculty_query(rewritten_query)

    # =========================
    # NOTIFICATIONS
    # =========================
    admission_keywords = ["admission", "fee", "eligibility", "course"]

    if any(k in rewritten_query.lower() for k in admission_keywords):
        notifications = search_notifications()

    # =========================
    # FACULTY SEARCH
    # =========================
    # =========================
    # FACULTY SEARCH
    # =========================
    faculty_rows = []

    # Decide what subject to use
    if subject:
        clean_query = normalize_subject(subject)
    elif session_id in last_subject_by_session:
        # Reuse last subject if analyzer missed it
        clean_query = last_subject_by_session[session_id]
    else:
        clean_query = clean_faculty_query(rewritten_query)

    # Run faculty search if intent is faculty OR if user asked a follow-up (where/when/room/time)
    if intent == "faculty" or any(word in query for word in ["where", "when", "room", "time"]):
        faculty_rows = search_faculty(clean_query)

    row = faculty_rows[0] if faculty_rows else None

    if row:
        # Always update session memory with the subject
        last_subject_by_session[session_id] = row.subject_name.lower()

        if "who" in query or "teacher" in query:
            return f"{row.subject_name} is taught by {row.faculty_name}."

        if "time" in query or "when" in query:
            return f"{row.subject_name} is scheduled at {row.time_slot}."

        if "room" in query or "where" in query:
            return f"{row.subject_name} is in room {row.room_number}."


    # =========================
    # BUILD CONTEXT
    # =========================
    context_chunks = [r.content.strip() for r in docs if r.content]

    if not context_chunks and not faculty_rows:
        # Guard clause: if user asked "where" but no subject context exists
        if any(word in query for word in followup_words) and session_id not in last_subject_by_session:
            return "Please specify the subject (e.g., 'Where is Python class?')."
        return "Sorry, I cannot find relevant information in the college documents."

    document_context = "\n\n".join(context_chunks)[:12000]

    notification_context = "\n\n".join(
        [f"{n.title} - {n.summary}" for n in notifications]
    )

    history_text = "\n".join([f"{h.role}: {h.message}" for h in history])

    prompt = f"""
You are an AI assistant for Cluster University.

Instructions:

1. Answer ONLY from DOCUMENT CONTEXT and NOTIFICATIONS.
2. Do not invent facts.
3. If the answer is not available, say:
   "I couldn't find that information in the university documents."
4. Prefer DOCUMENT CONTEXT over general knowledge.
5. If CHAT HISTORY helps resolve pronouns like "it" or "that", use it.
6. Answer naturally in 2-5 sentences.
7. If multiple relevant documents exist, combine them into one coherent answer.

--------------------

CHAT HISTORY
{history}

DOCUMENT CONTEXT
{context}

NOTIFICATIONS
{notifications}

QUESTION
{question}

ANSWER:
"""
    # =========================
    # LLM CALL (ONLY HERE)
    # =========================
    for attempt in range(3):
        try:
            return generate_llm_response(prompt)
        except Exception as e:
            print(f"Retry {attempt+1}/3 failed:", e)
            time.sleep(2)

    return "Sorry, AI service is currently unavailable."