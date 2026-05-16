from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text
from datetime import datetime

from app.services.chat_service import generate_response
from app.db.database import engine

router = APIRouter()


# =========================
# REQUEST MODEL
# =========================
class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message
    session_id = request.session_id

# =========================
# CREATE / UPDATE SESSION
# =========================
    with engine.begin() as conn:

        result = conn.execute(
            text("""
                INSERT INTO sessions
                (session_id, last_seen)
                VALUES
                (:session_id, NOW())

                ON CONFLICT (session_id)
                DO UPDATE SET last_seen = NOW()
            """),
            {
                "session_id": session_id
            }
        )

    print("SESSION UPSERT EXECUTED")

    # =========================
    # SAVE USER MESSAGE
    # =========================
    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO chat_history
                (session_id, role, message, created_at)
                VALUES
                (:session_id, 'user', :message, :created_at)
            """),
            {
                "session_id": session_id,
                "message": user_message,
                "created_at": datetime.utcnow()
            }
        )

    # =========================
    # GENERATE AI RESPONSE
    # =========================
    response = generate_response(
        user_message,
        session_id
    )

    # =========================
    # SAVE ASSISTANT RESPONSE
    # =========================
    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO chat_history
                (session_id, role, message, created_at)
                VALUES
                (:session_id, 'assistant', :message, :created_at)
            """),
            {
                "session_id": session_id,
                "message": response,
                "created_at": datetime.utcnow()
            }
        )

    return {
        "response": response
    }