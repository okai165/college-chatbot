from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding
from app.crawler.pdf_parser import parse_notice_metadata

def admission_exists(source_url):
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


def save_admission(title, date, source_url, content):
    try:
        print("\n========== SAVE_ADMISSION ==========")
        print("TITLE:", title)

        full_text = f"""
TITLE:
{title}

DATE:
{date}

SOURCE:
{source_url}

CONTENT:
{content}
"""

        print("Generating embedding...")
        embedding = generate_embedding(full_text)
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        # Extract metadata (semester, exam_type, batch, issued_date)
        metadata = parse_notice_metadata(full_text)

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
                        :semester,
                        :exam_type,
                        :batch,
                        :issued_date
                    )
                """),
                {
                    "content": full_text,
                    "doc_type": "admission",
                    "embedding": embedding_str,
                    "document_name": title,
                    "semester": metadata.get("semester"),
                    "exam_type": metadata.get("exam_type"),
                    "batch": metadata.get("batch"),
                    "issued_date": metadata.get("issued_date")
                }
            )

        print(f"Saved Admission Doc: {title}")

    except Exception as e:
        print("ADMISSION SAVE ERROR:", e)
