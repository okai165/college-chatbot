from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding


def retrieve_similar_chunks(query: str):

    try:

        query_embedding = generate_embedding(query)

        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        with engine.connect() as conn:

            # Find best matching document
            best_match = conn.execute(
                text("""
                    SELECT
                        document_name,
                        embedding <-> CAST(:query_embedding AS vector) AS distance
                    FROM documents
                    ORDER BY embedding <-> CAST(:query_embedding AS vector)
                    LIMIT 1
                """),
                {
                    "query_embedding": query_embedding_str
                }
            ).fetchone()

            if not best_match:
                return []
            # reject unrelated matches
            if best_match.distance > 1.20:
                print("No relevant document found")
                return []
            
            print("\n========== BEST DOCUMENT ==========")
            print(best_match.document_name)
            print("Distance:", best_match.distance)

            # Fetch ALL chunks from that document
            if best_match.document_name:

                result = conn.execute(
                    text("""
                        SELECT content
                        FROM documents
                        WHERE document_name = :document_name
                        ORDER BY id
                    """),
                    {
                        "document_name": best_match.document_name
                    }
                )

            else:

                result = conn.execute(
                    text("""
                        SELECT content
                        FROM documents
                        ORDER BY embedding <-> CAST(:query_embedding AS vector)
                        LIMIT 10
                    """),
                    {
                        "query_embedding": query_embedding_str
                    }
                )
            rows = result.fetchall()

        print("\n========== RETURNING FULL DOCUMENT ==========\n")

        for i, row in enumerate(rows):
            print(f"\nCHUNK {i+1}")
            print(row.content[:500])

        return rows

    except Exception as e:

        print("❌ RETRIEVER ERROR:", e)
        return []