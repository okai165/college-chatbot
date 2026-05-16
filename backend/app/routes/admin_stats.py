from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.db.database import engine
from app.routes.admin_auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(username: str = Depends(require_admin)):

    with engine.begin() as conn:

        total_sessions = conn.execute(
            text("SELECT COUNT(*) FROM sessions")
        ).scalar()

        total_messages = conn.execute(
            text("SELECT COUNT(*) FROM chat_history")
        ).scalar()

        active_sessions = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM sessions
                WHERE last_seen > NOW() - INTERVAL '10 minutes'
            """)
        ).scalar()

    return {
        "admin": username,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_messages": total_messages
    }