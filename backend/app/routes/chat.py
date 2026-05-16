from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.services.chat_service import generate_response
from app.db.database import engine

router = APIRouter()

# ✅ REQUEST MODEL
class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.post("/chat")
def chat(request: ChatRequest):

    # 1. Save user message
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO chat_history (session_id, role, message)
                VALUES (:session_id, 'user', :message)
            """),
            {
                "session_id": request.session_id,
                "message": request.message
            }
        )

    # 2. Generate response (RAG + memory)
    response = generate_response(
        request.message,
        request.session_id
    )

    # 3. Save assistant message
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO chat_history (session_id, role, message)
                VALUES (:session_id, 'assistant', :message)
            """),
            {
                "session_id": request.session_id,
                "message": response
            }
        )

    return {"response": response}