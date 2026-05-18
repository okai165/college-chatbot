from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding


# =========================
# RETRIEVE SIMILAR CHUNKS
# =========================
def retrieve_similar_chunks(query: str):

    try:
        # Generate embedding
        query_embedding = generate_embedding(query)

        # Convert embedding list → pgvector format
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT 
                        content,
                        embedding <-> CAST(:query_embedding AS vector) AS distance
                    FROM documents
                    ORDER BY embedding <-> CAST(:query_embedding AS vector)
                    LIMIT 5
                """),
                {
                    "query_embedding": query_embedding_str
                }
            )

            rows = result.fetchall()

        # =========================
        # DEBUG OUTPUT
        # =========================
        print("\n========== RETRIEVED CHUNKS ==========\n")

        for i, row in enumerate(rows):

            print(f"RESULT {i+1}")
            print("DISTANCE:", row.distance)

            if row.content:
                print(row.content[:500])

            print("\n-----------------------------------\n")

        return rows

    except Exception as e:

        print("❌ RETRIEVER ERROR:", e)

        return []