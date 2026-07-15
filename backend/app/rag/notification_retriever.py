from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding

def notification_exists(source_url):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 1
                FROM documents
                WHERE content LIKE :url
                LIMIT 1
            """),
            {"url": f"%{source_url}%"}
        )
        return result.fetchone() is not None


def save_notification(data):
    try:
        print("\n========== SAVE_NOTIFICATION ==========")
        print("TITLE:", data.get("title"))

        full_text = f"""

TITLE:
{data.get("title")}


TYPE:
Official Admission Notification


DETAILS:
{data.get("summary")}


ELIGIBILITY:
{data.get("eligibility")}


IMPORTANT DATES:

Application Start Date:
{data.get("start_date")}

Last Date:
{data.get("last_date")}


SOURCE:
{data.get("source_url")}

"""

        print("Generating embedding...")
        embedding = generate_embedding(full_text)
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        with engine.begin() as conn:
            # Insert into unified documents table
            conn.execute(
                text("""
                    INSERT INTO documents
                    (
                        content,
                        doc_type,
                        embedding,
                        document_name,
                        semester,
                        exam_type,
                        batch,
                        issued_date
                    )
                    VALUES
                    (
                        :content,
                        :doc_type,
                        CAST(:embedding AS vector),
                        :document_name,
                        NULL,
                        NULL,
                        NULL,
                        :issued_date
                    )
                """),
                {
                    "content": full_text,
                    "doc_type": "notification",
                    "embedding": embedding_str,
                    "document_name": data.get("title"),
                    "issued_date": data.get("start_date")
                }
            )

        print(f"Saved Notification Doc: {data.get('title')}")

    except Exception as e:
        print("NOTIFICATION SAVE ERROR:", e)


def search_notifications(query):
    with engine.connect() as conn:

        result = conn.execute(
            text("""
            SELECT
                title,
                summary,
                eligibility,
                start_date,
                last_date
            FROM notifications
            WHERE
            title ILIKE :query
            OR summary ILIKE :query
            ORDER BY id DESC
            LIMIT 10
            """),
            {
                "query": f"%{query}%"
            }
        )

        return result.fetchall()