from collections import Counter


def detect_doc_type(rows):

    types = [
        row.doc_type
        for row in rows
        if row.doc_type
    ]

    if not types:
        return None

    return Counter(types).most_common(1)[0][0]