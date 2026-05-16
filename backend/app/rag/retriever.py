from sqlalchemy import text

from app.db.database import engine
from app.rag.embedder import generate_embedding


def retrieve_similar_chunks(query, limit=3):
    query_embedding = generate_embedding(query)

    sql = text("""
        SELECT content,
        embedding <=> CAST(:embedding AS vector) AS distance
        FROM documents
        ORDER BY distance
        LIMIT :limit
    """)

    with engine.connect() as connection:

        results = connection.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "limit": limit
            }
        )

        return results.fetchall()