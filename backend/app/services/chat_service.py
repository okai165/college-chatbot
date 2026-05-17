from sqlalchemy import text
from app.db.database import engine
from app.rag.retriever import retrieve_similar_chunks
from app.services.llm import client


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

    # oldest → newest
    return rows[::-1]


# =========================
# MAIN RAG FUNCTION
# =========================
def generate_response(user_query, session_id):

    # =========================
    # RETRIEVE DOCUMENTS
    # =========================
    docs = retrieve_similar_chunks(user_query)

    print("RETRIEVED DOCS:", docs)

    # =========================
    # BUILD CONTEXT
    # =========================
    context_chunks = [
        d["content"].strip()
        for d in docs
        if d.get("content")
    ]

    context = "\n\n".join(context_chunks)

    print("CONTEXT:", context[:500])

    # =========================
    # STRICT GUARD
    # =========================
    if len(context_chunks) == 0:

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
    # PROMPT
    # =========================
    prompt = f"""
You are a strict college assistant chatbot.

RULES:
- Answer ONLY from the provided CONTEXT
- Never use outside knowledge
- If answer is missing from context, say exactly:
  "Sorry, I cannot find relevant information in the college documents."
- Keep responses short and factual

CHAT HISTORY:
{memory_text}

CONTEXT:
{context}

USER QUESTION:
{user_query}
"""

    # =========================
    # GEMINI RESPONSE
    # =========================
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text