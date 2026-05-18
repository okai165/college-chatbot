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

    return rows[::-1]


# =========================
# MAIN RAG FUNCTION
# =========================
def generate_response(user_query, session_id):

    try:

        # =========================
        # RETRIEVE DOCUMENTS
        # =========================
        docs = retrieve_similar_chunks(user_query)

        print("\n========== RETRIEVED DOCS ==========")
        print(docs)

        # =========================
        # BUILD CONTEXT
        # =========================
        context_chunks = []

        for row in docs:

            if row.content:

                cleaned = row.content.strip()

                if cleaned:
                    context_chunks.append(cleaned)

        context = "\n\n".join(context_chunks)

        print("\n========== FINAL CONTEXT ==========")
        print(context[:1000])

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
        # GEMINI RESPONSE
        # =========================
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        print("\n========== GEMINI RESPONSE ==========\n")
        print(response.text)

        return response.text

    except Exception as e:

        print("\n❌ CHAT SERVICE ERROR:", e)

        return (
            "Server error occurred while processing your request."
        )