from sqlalchemy import text

from app.db.database import engine
from app.rag.embedder import generate_embedding


# =========================
# CONFIG
# =========================
TOP_K = 5
SIMILARITY_THRESHOLD = 0.35


# =========================
# VECTOR RETRIEVAL
# =========================
def retrieve_similar_chunks(query: str):

    # Generate embedding
    query_embedding = generate_embedding(query)

    # Convert embedding list → pgvector string
    query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

    # Query database
    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    content,
                    embedding <-> CAST(:query_embedding AS vector) AS distance
                FROM documents
                ORDER BY embedding <-> CAST(:query_embedding AS vector)
                LIMIT 20
            """),
            {
                "query_embedding": query_embedding_str
            }
        )

        rows = result.fetchall()

    # =========================
    # FILTER RESULTS
    # =========================
    filtered_chunks = []

    for row in rows:

        distance = row.distance
        print("DISTANCE:", distance)

        if distance < 1.5:

            filtered_chunks.append({
                "content": row.content,
                "score": distance
            })

    # Sort best matches first
    filtered_chunks = sorted(
        filtered_chunks,
        key=lambda x: x["score"],
        reverse=True
    )

    # Return top results
    return filtered_chunks[:TOP_K]