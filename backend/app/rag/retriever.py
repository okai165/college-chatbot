from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding


def retrieve_similar_chunks(query: str, semester: str = None, exam_type: str = None, doc_type: str = None):
    try:
        query_embedding = generate_embedding(query)
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        # Build WHERE clause dynamically
        filters = []
        if semester:
            filters.append("semester = :semester")
        if exam_type:
            filters.append("exam_type = :exam_type")
        if doc_type:
            filters.append("doc_type = :doc_type")

        filter_clause = ""
        if filters:
            filter_clause = " AND " + " AND ".join(filters)

        with engine.connect() as conn:
            result = conn.execute(
                text(f"""
                    SELECT
                        content,
                        document_name,
                        semester,
                        exam_type,
                        doc_type,
                        embedding <-> CAST(:query_embedding AS vector) AS distance
                    FROM documents
                    WHERE content IS NOT NULL {filter_clause}
                    ORDER BY embedding <-> CAST(:query_embedding AS vector)
                    LIMIT 20
                """),
                {
                    "query_embedding": query_embedding_str,
                    "semester": semester,
                    "exam_type": exam_type,
                    "doc_type": doc_type
                }
            )

            rows = result.fetchall()
            print("\n===== RAW RESULTS =====")

            for row in rows:
                print(
                    row.document_name,
                    row.doc_type,
                    row.distance
                )
           # rows = [r for r in rows if r.distance < 0.9]S

            print("\n========== RETRIEVED DOCUMENTS ==========\n")
            for row in rows:
                print("DOCUMENT:", row.document_name)
                print("SEMESTER:", row.semester)
                print("EXAM TYPE:", row.exam_type)
                print("DOC TYPE:", row.doc_type)
                print("DISTANCE:", row.distance)
                print("CONTENT:")
                print(row.content[:500])
                print("=" * 100)

            if not rows:
                return []

            print("\n========== TOP MATCHES ==========\n")
            for i, row in enumerate(rows):
                print(
                    f"{i+1}. "
                    f"{row.document_name} | "
                    f"semester={row.semester} | "
                    f"exam_type={row.exam_type} | "
                    f"doc_type={row.doc_type} | "
                    f"distance={row.distance:.4f}"
                )

            return rows

    except Exception as e:
        print("❌ RETRIEVER ERROR:", e)
        return []