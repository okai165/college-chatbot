from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.db.database import engine
from app.routes.admin_auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


# =========================
# ADMIN STATS (FOOTPRINT KPIs)
# =========================
@router.get("/stats")
def get_stats(username: str = Depends(require_admin)):

    with engine.begin() as conn:

        total_sessions = conn.execute(text("""
            SELECT COUNT(*) FROM sessions
        """)).scalar()

        total_messages = conn.execute(text("""
            SELECT COUNT(*) FROM chat_history
        """)).scalar()

        active_sessions = conn.execute(text("""
            SELECT COUNT(*)
            FROM sessions
            WHERE last_seen > NOW() - INTERVAL '10 minutes'
        """)).scalar()

        # 🔥 FOOTPRINT METRIC
        avg_messages_per_session = conn.execute(text("""
            SELECT COALESCE(AVG(msg_count), 0)
            FROM (
                SELECT COUNT(*) AS msg_count
                FROM chat_history
                GROUP BY session_id
            ) sub
        """)).scalar()

    return {
        "admin": username,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_messages": total_messages,
        "avg_messages_per_session": round(avg_messages_per_session, 2)
    }


# =========================
# RECENT CHATS
# =========================
@router.get("/recent-chats")
def recent_chats():

    with engine.begin() as conn:
        result = conn.execute(text("""
            SELECT session_id, role, message, created_at
            FROM chat_history
            ORDER BY created_at DESC
            LIMIT 20
        """))

        return [dict(row._mapping) for row in result]