from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding
from app.crawler.pdf_parser import parse_notice_metadata


# ==========================
# CHECK IF DOCUMENT EXISTS
# ==========================
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


# ==========================
# SIMPLE WORD CHUNKER
# ==========================
def chunk_text(text, chunk_size=400, overlap=80):
    """
    Split text into overlapping chunks.

    chunk_size = number of words
    overlap = repeated words between chunks
    """

    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size

        chunks.append(" ".join(words[start:end]))

        if end >= len(words):
            break

        start = end - overlap

    return chunks


# ==========================
# SAVE DOCUMENT
# ==========================
def save_document(
    title,
    date,
    source_url,
    content,
    doc_type="notice"
):
    try:

        print("\n========== SAVE DOCUMENT ==========")
        print("TITLE:", title)
        print("DOC TYPE:", doc_type)
        print("SOURCE:", source_url)

        metadata = {}

        if doc_type == "admission":
            metadata = parse_notice_metadata(content)

        chunks = chunk_text(content)

        print(f"Created {len(chunks)} chunks")

        source_type = (
            "pdf"
            if source_url.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx"))
            else "html"
        )

        with engine.begin() as conn:

            for i, chunk in enumerate(chunks, start=1):

                full_text = f"""
TITLE:
{title}

SOURCE:
{source_url}

CHUNK:
{i}/{len(chunks)}

CONTENT:
{chunk}
"""

                print(f"Embedding chunk {i}/{len(chunks)}")

                embedding = generate_embedding(full_text)
                embedding_str = "[" + ",".join(map(str, embedding)) + "]"

                conn.execute(
                    text("""
                        INSERT INTO documents
                        (
                            content,
                            embedding,
                            source_url,
                            source_title,
                            source_type,
                            document_name,
                            doc_type,
                            semester,
                            exam_type,
                            batch,
                            issued_date
                        )
                        VALUES
                        (
                            :content,
                            CAST(:embedding AS vector),
                            :source_url,
                            :source_title,
                            :source_type,
                            :document_name,
                            :doc_type,
                            :semester,
                            :exam_type,
                            :batch,
                            :issued_date
                        )
                    """),
                    {
                        "content": full_text,
                        "embedding": embedding_str,
                        "source_url": source_url,
                        "source_title": title,
                        "source_type": source_type,
                        "document_name": title,
                        "doc_type": doc_type,
                        "semester": metadata.get("semester"),
                        "exam_type": metadata.get("exam_type"),
                        "batch": metadata.get("batch"),
                        "issued_date": metadata.get("issued_date") or date,
                    }
                )

        print(f"Successfully saved {len(chunks)} chunks for '{title}'")

    except Exception as e:
        print("DOCUMENT SAVE ERROR:", e)