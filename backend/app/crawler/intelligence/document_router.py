from app.crawler.intelligence.embedding_classifier import classify_by_embedding

def route_document(title, text):
    combined = (title + " " + text[:2000])

    category, score = classify_by_embedding(combined)

    # confidence guard
    if score < 0.35:
        return "notice"

    return category