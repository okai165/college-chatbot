from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding

def save_notice(title, source_url, content):
    try:
        print("\n========== SAVE_NOTICE ==========")
        print("TITLE:", title)

        full_text = f"""
TITLE:
{title}

SOURCE:
{source_url}

CONTENT:
{content}
"""

        print("Generating embedding...")
        embedding = generate_embedding(full_text)
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        with engine.begin() as conn:
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
                        NULL
                    )
                """),
                {
                    "content": full_text,
                    "doc_type": "notice",   # distinguish from admissions
                    "embedding": embedding_str,
                    "document_name": title
                }
            )

        print(f"Saved Notice Doc: {title}")

    except Exception as e:
        print("NOTICE SAVE ERROR:", e)
