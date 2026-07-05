from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

CATEGORIES = {
    "admission": [
        "admission merit list counselling spot round selection list FYUGP intake"
    ],
    "fee": [
        "fee structure college fee tuition fee payment schedule"
    ],
    "scholarship": [
        "scholarship financial assistance PMSSS national scholarship"
    ],
    "examination": [
        "exam datesheet result revaluation internal assessment"
    ],
    "nirf": [
        "NIRF ranking institutional ranking framework ministry of education"
    ],
    "iqac": [
        "internal quality assurance IQAC report accreditation NAAC"
    ],
    "notice": [
        "general notice circular announcement update office order"
    ]
}

category_embeddings = {
    k: model.encode(v[0]) for k, v in CATEGORIES.items()
}


def classify_by_embedding(text: str):
    text_vec = model.encode(text[:2000])

    best_cat = "notice"
    best_score = -1

    for cat, vec in category_embeddings.items():
        score = np.dot(text_vec, vec) / (
            np.linalg.norm(text_vec) * np.linalg.norm(vec)
        )

        if score > best_score:
            best_score = score
            best_cat = cat

    return best_cat, float(best_score)