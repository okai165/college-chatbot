from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding
from app.crawler.pdf_parser import parse_notice_metadata  # still used for admissions


def document_exists(source_url):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 1
                FROM documents
                WHERE source_url = :url
                LIMIT 1
            """),
            {"url": source_url}
        )
        return result.fetchone() is not None


def save_document(
    title,
    date,
    source_url,
    content,
    doc_type="notice"   # default type is 'notice' for HTML pages
):
    try:
        print("\n========== SAVE_DOCUMENT ==========")
        print("TITLE:", title)
        print("DOC_TYPE:", doc_type)
        print("SOURCE_URL:", source_url)

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

        # Extract metadata only for admissions/exams
        metadata = {}
        if doc_type == "admission":
            metadata = parse_notice_metadata(full_text)

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO documents
                    (
                        content,
                        doc_type,
                        embedding,
                        document_name,
                        source_url,
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
                        :source_url,
                        :semester,
                        :exam_type,
                        :batch,
                        :issued_date
                    )
                """),
                {
                    "content": full_text,
                    "doc_type": doc_type,
                    "embedding": embedding_str,
                    "document_name": title,
                    "source_url": source_url,
                    "semester": metadata.get("semester"),
                    "exam_type": metadata.get("exam_type"),
                    "batch": metadata.get("batch"),
                    "issued_date": metadata.get("issued_date") or date
                }
            )

        print(f"Saved {doc_type} Doc: {title}")

    except Exception as e:
        print("DOCUMENT SAVE ERROR:", e)