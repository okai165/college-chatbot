from sentence_transformers import CrossEncoder

# Loads once when the server starts
reranker = CrossEncoder(
    "BAAI/bge-reranker-v2-m3"
)
reranker.model.eval()

def rerank(query, rows, top_k=5):
    """
    rows = SQLAlchemy rows returned by retrieve_global_chunks()
    """

    if not rows:
        return []

    pairs = [
        (
            query,
            f"""
    TITLE:
    {row.title}

    TYPE:
    {row.doc_type}

    CONTENT:
    {row.content[:2000]}
    """
        )
        for row in rows
    ]

    scores = reranker.predict(
        pairs,
        show_progress_bar=False
    )

    ranked = sorted(
        zip(rows, scores),
        key=lambda x: float(x[1]),
        reverse=True
    )

    print("\n===== CROSS ENCODER SCORES =====")

    for row, score in ranked:
        print(
            row.title,
            row.doc_type,
            round(float(score), 3)
        )

    return ranked[:top_k]