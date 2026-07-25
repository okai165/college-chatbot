from sqlalchemy import text
from app.db.database import engine

from app.rag.retrieval_pipeline import (
    retrieve_with_routing
)
from app.services.llm import generate_llm_response

from app.rag.notification_retriever import search_notifications
from app.rag.query_analyzer import analyze_query

from app.services.faculty_service import handle_faculty_query
from app.services.quick_link_service import search_quick_link
from app.handlers.greeting_handler import handle_greeting
from app.handlers.casual_handler import handle_casual_query
from app.handlers.acknowledgement_handler import handle_acknowledgement
from app.handlers.farewell_handler import handle_farewell
import time
import re

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
# QUERY REWRITER
# =========================

def rewrite_query(user_query, history):

    memory_text = "\n".join(
        [
            f"{h.role}: {h.message}"
            for h in history
        ]
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

        rewritten_query = generate_llm_response(
            prompt
        ).strip()


        print("\n========== REWRITTEN QUERY ==========")
        print(rewritten_query)


        return rewritten_query


    except Exception:

        return user_query



# =========================
# MAIN RESPONSE GENERATOR
# =========================

def generate_response(user_query, session_id):


    query = user_query.lower().strip()
    # =========================
    # QUERY NORMALIZATION
    # =========================

    query = re.sub(r"\s+", " ", query)
    query = query.strip("!?.,")

    notifications = []

    # =========================
    # CONVERSATIONAL HANDLERS
    # =========================

    handlers = [

        handle_greeting,
        handle_farewell,
        handle_casual_query,
        handle_acknowledgement

    ]


    for handler in handlers:

        response = handler(query)

        if response:
            return response
        # =========================
    # QUICK LINKS
    # =========================

    portal_keywords = [

        "student login",
        "login portal",
        "know your timetable",
        "know your time table",
        "open timetable",
        "open time table",
        "know your roll no",
        "know your roll number",
        "roll no portal",
        "roll number portal"

    ]


    if any(
        k in query
        for k in portal_keywords
    ):


        quick_link = search_quick_link(
            user_query
        )


        if quick_link:

            return (
                f"{quick_link.title}\n\n"
                f"You can access it here:\n"
                f"{quick_link.url}"
            )




    # =========================
    # CHAT HISTORY
    # =========================

    history = get_chat_history(
        session_id
    )



    # =========================
    # FOLLOW UP DETECTION
    # =========================

    FOLLOW_UP_WORDS = {

        "where",
        "when",
        "room",
        "time",
        "location",
        "lab",
        "timing",
        "schedule"

    }


    is_followup = any(
        re.search(rf"\b{re.escape(word)}\b", query)
        for word in FOLLOW_UP_WORDS
    )



    if is_followup:

        rewritten_query = rewrite_query(
            user_query,
            history
        )

    else:

        rewritten_query = user_query




    # =========================
    # QUERY ANALYSIS
    # =========================

    analysis = analyze_query(
        rewritten_query
    )


    intent = analysis.get(
        "intent"
    )


    subject = analysis.get(
        "subject"
    )


    print(
        "\n========== QUERY ANALYZER =========="
    )

    print(
        analysis
    )




    # =========================
    # FACULTY HANDLER
    # =========================

    if (
        intent == "faculty"
        or is_followup
    ):


        faculty_response = handle_faculty_query(

            query=user_query,

            intent=intent,

            subject=subject,

            operation=analysis.get("operation"),

            session_id=session_id

        )


        if faculty_response:

            return faculty_response



    # =========================
    # RAG RETRIEVAL
    # =========================


    query_text = " ".join(
        filter(None, [rewritten_query, subject])
    )



    docs = retrieve_with_routing(

        query=query_text,

        semester=analysis.get(
            "semester"
        ),

        exam_type=analysis.get(
            "exam_type"
        )

    )
    if not docs:
        return (
            "Sorry, I couldn't find relevant information "
            "in the university documents."
        )
    print("\n========== CONTEXT SENT TO LLM ==========\n")

    for i, (row, score) in enumerate(docs, start=1):

        print(f"\nChunk {i}")
        print("=" * 80)

        m = row._mapping

        print("TYPE:", type(row))

        print(
            "TITLE:",
            m.get("title") or m.get("document_name")
        )

        print(
            "DOC TYPE:",
            m.get("doc_type")
        )

        print(
            "SOURCE:",
            m.get("source_url")
        )

        print(
            "RERANK SCORE:",
            round(float(score), 3)
        )

        print("\nCONTENT:")

        content = m.get("content")

        if content:
            print(content[:300])
    # =========================
    # NOTIFICATIONS
    # =========================

    admission_keywords = [

        "admission",
        "apply",
        "application",
        "eligibility",
        "fee",
        "cuet",
        "selection",
        "procedure"

    ]


    if any(k in rewritten_query.lower() for k in admission_keywords):
        notifications = search_notifications(rewritten_query)


    # =========================
    # BUILD CONTEXT
    # =========================

    context_chunks = []

    for i, (row, score) in enumerate(docs, start=1):

        m = row._mapping

        content = m.get("content")

        if not content:
            continue

        context_chunks.append(
            f"""
        === PASSAGE {i} ===

        {content[:6000].strip()}
        """
        )
    if not context_chunks:

        return (
            "Sorry, I cannot find relevant "
            "information in the college documents."
        )


    document_context = "\n\n".join(
        context_chunks
    )


    notification_context = "\n\n".join(

        [

            f"{n.title} - {n.summary}"

            for n in notifications

        ]

    )



    history_text = "\n".join(

        [

            f"{h.role}: {h.message}"

            for h in history

        ]

    )



    # =========================
    # FINAL PROMPT
    # =========================

    prompt = f"""

You are an AI assistant for Government College for Women.


Rules:

- Answer ONLY using the official sources provided below.
- Do not use outside knowledge.
- If the answer exists in any source, extract it.
- Do not say "information unavailable" when relevant information exists.
- Do not mention documents, passages, chunks, sources, or retrieval.
- Give a direct student-friendly answer.


DOCUMENT PASSAGES:

{document_context}


OFFICIAL NOTIFICATIONS:

{notification_context}


QUESTION:

{query}


ANSWER:

"""
    
   




    # =========================
    # LLM CALL
    # =========================
    print("\n" + "=" * 100)
    print("PROMPT SENT TO LLM")
    print("=" * 100)
    print(prompt)
    print("=" * 100 + "\n")

    for attempt in range(3):

        try:

            response = generate_llm_response(prompt)

            print("\n========== LLM RESPONSE ==========")
            print(response)
            print("==================================")

            return response


        except Exception as e:

            print(
                f"Retry {attempt+1}/3 failed:",
                e
            )

            time.sleep(2)



    return (
        "Sorry, AI service is currently unavailable."
    )