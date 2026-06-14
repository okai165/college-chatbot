from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding


def retrieve_similar_chunks(query: str):
    try:
        query_embedding = generate_embedding(query)
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT
                        content,
                        document_name,
                        embedding <-> CAST(:query_embedding AS vector) AS distance
                    FROM documents
                    ORDER BY embedding <-> CAST(:query_embedding AS vector)
                    LIMIT 8
                """),
                {
                    "query_embedding": query_embedding_str
                }
            )

            rows = result.fetchall()

            if not rows:
                return []

            print("\n========== TOP MATCHES ==========\n")
            for i, row in enumerate(rows):
                print(
                    f"{i+1}. "
                    f"{row.document_name} | "
                    f"distance={row.distance:.4f}"
                )

            # Return only the top matches
            return rows

    except Exception as e:
        print("❌ RETRIEVER ERROR:", e)
        return []
