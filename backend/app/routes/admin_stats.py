from fastapi import APIRouter, Depends, Query
from sqlalchemy import text

from app.db.database import engine
from app.routes.admin_auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    username: str = Depends(require_admin),
    days: int = Query(1, ge=1, le=30)  # default 1 day, allow 1..30
):
    with engine.begin() as conn:

        # Sessions started within last N days
        total_sessions = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM sessions
                WHERE started_at >= NOW() - (:days || ' days')::interval
            """),
            {"days": days}
        ).scalar()

        # Messages within last N days
        total_messages = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM chat_history
                WHERE created_at >= NOW() - (:days || ' days')::interval
            """),
            {"days": days}
        ).scalar()

        # Active sessions still based on last 10 minutes (live metric)
        active_sessions = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM sessions
                WHERE last_seen > NOW() - INTERVAL '10 minutes'
            """)
        ).scalar()

        # Avg messages per session within last N days
        avg_messages_per_session = conn.execute(
            text("""
                SELECT COALESCE(AVG(msg_count), 0)
                FROM (
                    SELECT session_id, COUNT(*) AS msg_count
                    FROM chat_history
                    WHERE created_at >= NOW() - (:days || ' days')::interval
                    GROUP BY session_id
                ) sub
            """),
            {"days": days}
        ).scalar()

    return {
        "admin": username,
        "days": days,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_messages": total_messages,
        "avg_messages_per_session": round(avg_messages_per_session, 2),
    }