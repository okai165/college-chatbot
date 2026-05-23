from fastapi import APIRouter, Depends, Query
from sqlalchemy import text

from app.db.database import engine
from app.routes.admin_auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    username: str = Depends(require_admin),
    days: int = Query(1, ge=1, le=30)
):

    with engine.begin() as conn:

        # =========================
        # MAIN STATS
        # =========================

        total_sessions = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM sessions
                WHERE started_at >= NOW() - (:days || ' days')::interval
            """),
            {"days": days}
        ).scalar()

        total_messages = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM chat_history
                WHERE created_at >= NOW() - (:days || ' days')::interval
            """),
            {"days": days}
        ).scalar()

        active_sessions = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM sessions
                WHERE last_seen > NOW() - INTERVAL '10 minutes'
            """)
        ).scalar()

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

        # =========================
        # GRAPH DATA
        # =========================

        messages_graph = conn.execute(
            text("""
                SELECT
                    DATE(created_at) AS day,
                    COUNT(*) AS total
                FROM chat_history
                WHERE created_at >= NOW() - (:days || ' days')::interval
                GROUP BY day
                ORDER BY day
            """),
            {"days": days}
        ).fetchall()

        sessions_graph = conn.execute(
            text("""
                SELECT
                    DATE(started_at) AS day,
                    COUNT(*) AS total
                FROM sessions
                WHERE started_at >= NOW() - (:days || ' days')::interval
                GROUP BY day
                ORDER BY day
            """),
            {"days": days}
        ).fetchall()

    return {
        "admin": username,
        "days": days,

        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_messages": total_messages,
        "avg_messages_per_session": round(
            avg_messages_per_session,
            2
        ),

        "messages_graph": [
            {
                "day": str(row.day),
                "total": row.total
            }
            for row in messages_graph
        ],

        "sessions_graph": [
            {
                "day": str(row.day),
                "total": row.total
            }
            for row in sessions_graph
        ]
    }