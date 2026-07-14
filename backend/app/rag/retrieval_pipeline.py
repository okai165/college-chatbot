from app.rag.retriever import retrieve_global_chunks
from app.rag.doc_type_router import detect_doc_type


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
    dominant_type = detect_doc_type(
        global_results
    )


    print(
        "\n===== DOMINANT DOC TYPE ====="
    )

    print(
        dominant_type
    )


    # Second focused search
    if dominant_type:

        focused_results = retrieve_global_chunks(
            query=query,
            doc_types=[dominant_type],
            semester=semester,
            exam_type=exam_type,
            limit=8
        )

        return focused_results


    return global_results[:5]