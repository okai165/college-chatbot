from sqlalchemy import text
from app.db.database import engine
from app.rag.retriever import retrieve_similar_chunks
from app.services.llm import client


# =========================
# OPTIONAL: CHAT MEMORY
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

    return rows[::-1]  # keep chronological order


# =========================
# MAIN RAG FUNCTION
# =========================
def generate_response(user_query, session_id):

    # 1. Retrieve relevant documents from vector DB
    docs = retrieve_similar_chunks(user_query)

    context = "\n".join([d.content for d in docs if d.content])

    # 2. 🔒 STRICT DOMAIN CHECK (VERY IMPORTANT)
    # If no meaningful context found → refuse immediately
    if not context or len(context.strip()) < 30:
        return "Sorry, I cannot find relevant information in the college documents."

    # 3. Optional: chat history (memory)
    history = get_chat_history(session_id)

    memory_text = "\n".join(
        [f"{h.role}: {h.message}" for h in history]
    ) if history else ""

    # 4. STRICT SYSTEM PROMPT (NO OUTSIDE KNOWLEDGE)
    prompt = f"""
You are a strict college assistant chatbot.

RULES:
- You MUST answer ONLY using the provided context
- If the answer is not in the context, respond exactly:
  "Sorry, I cannot find relevant information in the college documents."
- Do NOT use outside knowledge under any circumstances

CHAT HISTORY:
{memory_text}

COLLEGE CONTEXT:
{context}

USER QUESTION:
{user_query}
"""

    # 5. Call Gemini model
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text