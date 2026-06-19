from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding


def save_admission_document(
    title,
    date,
    pdf_url,
    content
):
    try:

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

        embedding = generate_embedding(full_text)

        embedding_str = (
            "[" +
            ",".join(map(str, embedding))
            + "]"
        )
        
        with engine.begin() as conn:
            # CHECK IF ALREADY EXISTS
            exists = conn.execute(
                text("""
                    SELECT 1
                    FROM documents
                    WHERE document_name = :name
                    LIMIT 1
                """),
                {
                    "name": title
                }
            ).fetchone()

            if exists:
                print(f"Already exists: {title}")
                return
           

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

            print("SAVE_ADMISSION_DOCUMENT CALLED")
            print("TITLE =", title)

    except Exception as e:

        print(
            "ADMISSION SAVE ERROR:",
            e
        )