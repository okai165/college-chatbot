from sqlalchemy import text
from app.db.database import engine
from app.rag.embedder import generate_embedding


def retrieve_global_chunks(
    query: str,
    doc_types: list = None,
    semester: str = None,
    exam_type: str = None,
    limit: int = 30,
):
    try:

        query_embedding = generate_embedding(query)

        query_embedding_str = (
            "[" + ",".join(map(str, query_embedding)) + "]"
        )


        filters = []


        if semester:
            filters.append(
                "semester = :semester"
            )


        if exam_type:
            filters.append(
                "exam_type = :exam_type"
            )


        if doc_types:
            filters.append(
                "doc_type = ANY(:doc_types)"
            )


        filter_clause = ""

        if filters:
            filter_clause = (
                " AND "
                + " AND ".join(filters)
            )


        with engine.connect() as conn:

            result = conn.execute(
                text(f"""

                SELECT

                    content,
                    document_name,
                    source_url,
                    semester,
                    exam_type,
                    doc_type,


                    embedding <-> 
                    CAST(:query_embedding AS vector)
                    AS vector_distance,


                    COALESCE(
                        ts_rank(
                            tsv,
                            plainto_tsquery('english', :query)
                        ),
                        0
                    )
                    AS keyword_score,


                    (
                        0.7 *
                        (
                            1 -
                            (
                                embedding <-> 
                                CAST(:query_embedding AS vector)
                            )
                        )
                        +
                        0.3 *
                        COALESCE(
                            ts_rank(
                                tsv,
                                plainto_tsquery(
                                    'english',
                                    :query
                                )
                            ),
                            0
                        )
                    )
                    AS hybrid_score


                FROM documents


                WHERE content IS NOT NULL

                {filter_clause}


                ORDER BY hybrid_score DESC


                LIMIT :limit


                """),
                {
                    "query_embedding": query_embedding_str,
                    "query": query,
                    "semester": semester,
                    "exam_type": exam_type,
                    "doc_types": doc_types,
                    "limit": limit,
                },
            )


            rows = result.fetchall()



        print("\n===== RAW HYBRID RESULTS =====")


        for row in rows:

            print(
                row.document_name,
                "|",
                row.doc_type,
                "| vector:",
                round(row.vector_distance, 4),
                "| keyword:",
                round(row.keyword_score or 0, 4),
                "| hybrid:",
                round(row.hybrid_score or 0, 4),
            )



        # keep only reliable results

        HYBRID_THRESHOLD = 0.001


        rows = [
            r
            for r in rows
            if (r.hybrid_score or 0) >= HYBRID_THRESHOLD
        ]


        # final top chunks

        rows = sorted(
            rows,
            key=lambda x: x.hybrid_score or 0,
            reverse=True
        )[:5]



        print(
            "\n========== FINAL RETRIEVED CHUNKS ==========\n"
        )


        for i, row in enumerate(rows, 1):

            print(
                f"\nChunk {i}"
            )

            print("=" * 80)

            print(
                "DOCUMENT :",
                row.document_name
            )

            print(
                "DOC TYPE :",
                row.doc_type
            )

            print(
                "HYBRID SCORE :",
                row.hybrid_score
            )

            print("-" * 80)

            print(
                row.content
            )

            print("=" * 80)



        return rows



    except Exception as e:

        print(
            "❌ HYBRID RETRIEVER ERROR:",
            e
        )

        return []