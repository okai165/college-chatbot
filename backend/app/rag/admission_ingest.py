from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding


def admission_exists(pdf_url):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT 1
                FROM documents
                WHERE content LIKE :url
                LIMIT 1
            """),
            {
                "url": f"%{pdf_url}%"
            }
        )

        return result.fetchone() is not None


def save_admission_document(
    title,
    date,
    pdf_url,
    content
):
    try:

        print("\n========== SAVE_ADMISSION_DOCUMENT ==========")
        print("TITLE:", title)

        full_text = f"""
TITLE:
{title}

DATE:
{date}

PDF:
{pdf_url}

CONTENT:
{content}
"""

        print("Generating embedding...")

        embedding = generate_embedding(full_text)

        embedding_str = (
            "[" +
            ",".join(map(str, embedding))
            + "]"
        )

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO documents
                    (
                        content,
                        doc_type,
                        embedding,
                        document_name
                    )
                    VALUES
                    (
                        :content,
                        :doc_type,
                        CAST(:embedding AS vector),
                        :document_name
                    )
                """),
                {
                    "content": full_text,
                    "doc_type": "admission",
                    "embedding": embedding_str,
                    "document_name": title
                }
            )

        print(f"Saved Admission Doc: {title}")

    except Exception as e:

        print("ADMISSION SAVE ERROR:", e)