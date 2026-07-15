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

    notifications = []



    # =========================
    # SMALL TALK
    # =========================

    if query in [
        "hi",
        "hello",
        "hey"
    ]:

        return "Hello! 👋 How can I help you today?"



    if query in [
        "bye",
        "goodbye"
    ]:

        return "Goodbye! Have a great day."




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
        word in query
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


    query_text = (
        rewritten_query
        + " "
        + (subject or "")
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
            print(content[:400])
    # =========================
    # NOTIFICATIONS
    # =========================

    admission_keywords = [

        "admission",
        "fee",
        "eligibility",
        "course"

    ]


    if any(

        k in rewritten_query.lower()

        for k in admission_keywords

    ):

        notifications = search_notifications()


    # =========================
    # BUILD CONTEXT
    # =========================

    context_chunks = []


    for row, score in docs:

        m = row._mapping

        content = m.get("content")

        if content:

            context_chunks.append(
                f"""
    TITLE:
    {m.get("title")}

    DOCUMENT TYPE:
    {m.get("doc_type")}

    RERANK SCORE:
    {float(score):.3f}

    SOURCE:
    {m.get("source_url")}

    CONTENT:

    {content.strip()}
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

You are an AI assistant for Cluster University.


Instructions:

1. The document context is already sorted by relevance.

2. The FIRST document is the most relevant.

3. Use the FIRST document as your primary source.

4. Only use later documents if the first document does not contain enough information.

5. Never replace specific information with generic information.

6. If eligibility criteria are present, list them exactly as stated.

7. Do not summarize generic admission instructions when a detailed eligibility table exists.

8. If the answer is not in the context, reply:
"I couldn't find that information in the university documents."


--------------------


CHAT HISTORY:

{history_text}



DOCUMENT CONTEXT:

{document_context}



NOTIFICATIONS:

{notification_context}



QUESTION:

{user_query}



ANSWER:

"""




    # =========================
    # LLM CALL
    # =========================

    for attempt in range(3):

        try:

            return generate_llm_response(
                prompt
            )


        except Exception as e:

            print(
                f"Retry {attempt+1}/3 failed:",
                e
            )

            time.sleep(2)



    return (
        "Sorry, AI service is currently unavailable."
    )