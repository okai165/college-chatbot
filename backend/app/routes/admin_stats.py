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
            """),
        ).scalar()

        total_messages = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM chat_history
                WHERE role = 'user'
                  AND created_at >= NOW() - (:days || ' days')::interval
            """),
            {"days": days}
        ).scalar()

        active_sessions = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM sessions
                WHERE last_seen > NOW() - INTERVAL '10 minutes'
            """),
            {"days": days}
        ).scalar()

        avg_messages_per_session = conn.execute(
            text("""
                SELECT COALESCE(AVG(msg_count), 0)
                FROM (
                    SELECT session_id,
                           COUNT(*) AS msg_count
                    FROM chat_history
                    WHERE created_at >= NOW() - (:days || ' days')::interval
                    GROUP BY session_id
                ) sub
            """),
            {"days": days}
        ).scalar()

        # =========================
        # TOTAL USERS
        # =========================

        total_users = conn.execute(
            text("""
                SELECT COUNT(DISTINCT session_id)
                FROM chat_history
                WHERE created_at >= NOW() - (:days || ' days')::interval
            """),
            {"days": days}
        ).scalar()

        # =========================
        # MOST ASKED TOPICS
        # =========================

        top_categories_result = conn.execute(
            text("""
                SELECT
                CASE
                    WHEN LOWER(message) LIKE '%exam%'
                         OR LOWER(message) LIKE '%examination%'
                         OR LOWER(message) LIKE '%result%'
                         OR LOWER(message) LIKE '%datesheet%'
                         OR LOWER(message) LIKE '%hall ticket%'
                    THEN 'Exams'

                    WHEN LOWER(message) LIKE '%faculty%'
                         OR LOWER(message) LIKE '%teacher%'
                         OR LOWER(message) LIKE '%teach%'
                         OR LOWER(message) LIKE '%class%'
                         OR LOWER(message) LIKE '%room%'
                         OR LOWER(message) LIKE '%classroom%'
                         OR LOWER(message) LIKE '%timing%'
                         OR LOWER(message) LIKE '%time%'
                         OR LOWER(message) LIKE '%schedule%'
                    THEN 'Faculty'

                    WHEN LOWER(message) LIKE '%syllabus%'
                         OR LOWER(message) LIKE '%subject%'
                    THEN 'Syllabus'

                    WHEN LOWER(message) LIKE '%admission%'
                         OR LOWER(message) LIKE '%admissions%'
                         OR LOWER(message) LIKE '%admit%'
                    THEN 'Admission'

                    WHEN LOWER(message) LIKE '%library%'
                    THEN 'Library'

                    WHEN LOWER(message) LIKE '%event%'
                         OR LOWER(message) LIKE '%workshop%'
                         OR LOWER(message) LIKE '%sports%'
                         OR LOWER(message) LIKE '%cultural%'
                    THEN 'Events'

                    ELSE 'Other'
                END AS category,
                COUNT(*) AS total
                FROM chat_history
                WHERE role = 'user'
                  AND created_at >= NOW() - (:days || ' days')::interval
                GROUP BY category
                ORDER BY total DESC
            """),
            {"days": days}
        ).fetchall()

        top_categories = [
            {"category": row.category, "total": row.total}
            for row in top_categories_result
        ]

        # =========================
        # GRAPH DATA
        # =========================

        messages_graph = conn.execute(
            text("""
                SELECT DATE(created_at) AS day, COUNT(*) AS total
                FROM chat_history
                WHERE created_at >= NOW() - (:days || ' days')::interval
                GROUP BY day
                ORDER BY day
            """),
            {"days": days}
        ).fetchall()

        sessions_graph = conn.execute(
            text("""
                SELECT DATE(started_at) AS day, COUNT(*) AS total
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
        "total_users": total_users,
        "total_messages": total_messages,
        "avg_messages_per_session": round(avg_messages_per_session, 2),
        "top_categories": top_categories,
        "messages_graph": [
            {"day": str(row.day), "total": row.total}
            for row in messages_graph
        ],
        "sessions_graph": [
            {"day": str(row.day), "total": row.total}
            for row in sessions_graph
        ]
    }
