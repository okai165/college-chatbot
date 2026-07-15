from app.rag.retriever import retrieve_global_chunks
from app.rag.doc_type_router import detect_doc_type
from app.rag.reranker import rerank


def retrieve_with_routing(
    query: str,
    semester: str = None,
    exam_type: str = None,
):

    # First broad search
    global_results = retrieve_global_chunks(
        query=query,
        semester=semester,
        exam_type=exam_type,
        limit=30
    )

    if not global_results:
        return []

    # Detect dominant document category
    dominant_type = detect_doc_type(global_results)

    print("\n===== DOMINANT DOC TYPE =====")
    print(dominant_type)

    # Second focused search
    if dominant_type:

        focused_results = retrieve_global_chunks(
            query=query,
            doc_types=[dominant_type],
            semester=semester,
            exam_type=exam_type,
            limit=30
        )
        if len(focused_results) < 5:
            focused_results = global_results
        # Rerank focused results
        reranked = rerank(
            query=query,
            rows=focused_results,
            top_k=5
        )


        print("\n===== RERANKED RESULTS =====")

        for i, (row, score) in enumerate(reranked, start=1):

            print("\nRank:", i)

            print("TITLE:", row.title)

            print("DOC TYPE:", row.doc_type)

            print("RERANK SCORE:", round(score, 3))

            print(
                "CONTENT:",
                row.content[:300]
            )

        return reranked

    # Fallback
    return rerank(
        query=query,
        rows=global_results,
        top_k=5
    )