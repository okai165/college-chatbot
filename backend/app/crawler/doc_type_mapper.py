from collections import defaultdict

def calculate_confidence(score):

    if score >= 80:
        return 0.95

    elif score >= 60:
        return 0.85

    elif score >= 40:
        return 0.70

    elif score >= 20:
        return 0.50

    else:
        return 0.30
def classification_result(dtype, score=100):

    return {
        "type": dtype,
        "score": score,
        "confidence": calculate_confidence(score)
    }
def map_doc_type(url: str, title: str, content: str = "") -> dict:
    url_lower = url.lower()
    title_lower = title.lower()
    content_lower = content[:10000].lower()

    # ============================================================
    # 1. ABSOLUTE URL RULES (Highest Priority)
    # ============================================================

    MODULE_MAPPING = {
        "id=21": "library",
        "id=40": "ncc",
        "id=41": "nss",
        "id=47": "disclosure",
        "id=48": "scholarship",
        "id=49": "hostel",
        "id=50": "research",
        "id=51": "innovation",
        "id=52": "about",
        "id=53": "examination",
        "id=54": "grievance",
        "id=57": "entrepreneurship",
        "id=59": "student_corner",
    }

    for module, dtype in MODULE_MAPPING.items():
        if module in url_lower:
            return classification_result(dtype, 100)

    EXACT_URLS = {
        "admissions.php": "admission",
        "iqac.php": "iqac",
        "grievances.php": "grievance",
    }

    for page, dtype in EXACT_URLS.items():
        if page in url_lower:
            return classification_result(dtype, 100)

    if "nirf" in url_lower:
        return classification_result("nirf",100)

    if "syllabus" in url_lower:
        return classification_result("syllabus", 100)

    # ============================================================
    # 2. KEYWORD WEIGHTS
    # ============================================================

    KEYWORDS = {

        "admission": {
            "admissions 2026": 20,
            "admissions 2025": 20,
            "admissions": 18,
            "admission committee": 18,
            "spot round": 18,
            "walk-in round": 18,
            "document checklist": 16,
            "application form": 14,
            "selection list": 14,
            "merit list": 14,
            "registration process": 12,
            "fyugp": 12,
            "admission": 8,
        },

        "eligibility": {

            "eligibility criteria": 22,
            "admission eligibility": 22,
            "minimum qualification": 20,
            "required qualification": 20,
            "who can apply": 18,
            "admission criteria": 18,
            "minimum marks": 16,
            "required subjects": 16,
            "eligible candidates": 16,
            "eligibility": 10,
            "eligible": 8,
            "qualification": 8,
            "criteria": 6,
            "10+2": 12,
            "graduation": 10,

        },

        "fee": {
            "fee structure": 20,
            "refund of fees": 18,
            "fee refund": 16,
            "fee payment": 14,
            "admission fee": 12,
            "fees": 4,
        },

        "scholarship": {
            "about the scholarship": 22,
            "scholarship scheme": 20,
            "financial assistance": 16,
            "national scholarship portal": 16,
            "nsp portal": 14,
            "stipend": 10,
            "scholarship": 6,
        },

        "hostel": {
            "about the hostel": 22,
            "hostel administration": 18,
            "hostel facility": 16,
            "residential facility": 14,
            "hostel": 6,
        },

        "library": {
            "central library": 22,
            "one nation one subscription": 20,
            "books collection": 18,
            "digital library": 16,
            "onos": 15,
            "library": 6,
        },

        "research": {
            "central research laboratory": 22,
            "research laboratory": 20,
            "research centre": 18,
            "research center": 18,
            "research project": 14,
            "publication": 10,
            "research": 5,
        },

        "innovation": {
            "innovation incubation lab": 22,
            "innovation and incubation": 20,
            "innovation lab": 18,
            "incubation centre": 18,
            "innovation": 8,
        },

        "entrepreneurship": {
            "entrepreneurship development": 22,
            "startup culture": 18,
            "business incubation": 16,
            "startup": 12,
            "entrepreneurship": 10,
        },

        "examination": {
            "examination cell": 22,
            "exam cell": 20,
            "semester examination": 18,
            "date sheet": 16,
            "datesheet": 16,
            "revaluation": 12,
            "result": 10,
        },

        "iqac": {
            "internal quality assurance cell": 25,
            "quality assurance": 15,
            "naac": 12,
            "iqac": 10,
        },

        "grievance": {
            "grievances redressal cell": 25,
            "internal complaints committee": 24,
            "sexual harassment": 20,
            "anti sexual harassment": 18,
            "complaint": 8,
            "grievance": 8,
        },

        "ncc": {
            "national cadet corps": 25,
            "girls bn ncc": 18,
            "cadet": 10,
            "ncc": 8,
        },

        "nss": {
            "national service scheme": 25,
            "nss volunteers": 18,
            "volunteer": 8,
            "nss": 8,
        },

        "faculty": {
            "faculty profile": 22,
            "faculty members": 18,
            "assistant professor": 16,
            "associate professor": 16,
            "department of": 8,
        },

        "student_corner": {
            "student corner": 22,
            "student login": 20,
            "know your roll": 18,
            "know your timetable": 18,
            "know your time table": 18,
            "roll number": 15,
            "roll no": 15,
            "time table": 12,
        },

        "disclosure": {
            "public self disclosure": 25,
            "self disclosure": 20,
            "ugc recognition": 15,
            "institutional development plan": 15,
        },

        "about": {
            "about us": 20,
            "about college": 18,
            "history of college": 18,
            "government college for women": 15,
            "established in 1950": 15,
        },

        "notice": {
            "notice board": 18,
            "notification": 12,
            "announcement": 10,
            "circular": 10,
            "notice": 6,
        },
    }

    # ============================================================
    # 3. WEIGHTED SCORING
    # ============================================================

    scores = defaultdict(int)

    for doc_type, words in KEYWORDS.items():

        # Longer phrases first
        for phrase, weight in sorted(
            words.items(),
            key=lambda x: len(x[0]),
            reverse=True,
        ):

            # URL (highest confidence)
            if phrase in url_lower:
                scores[doc_type] += weight * 5

            # Title
            if phrase in title_lower:
                scores[doc_type] += weight * 3

            # Content
            count = content_lower.count(phrase)

            if count:
                # first occurrence
                scores[doc_type] += weight

                # additional occurrences (capped)
                scores[doc_type] += min(count - 1, 3)

    # ============================================================
    # 4. DECIDE WINNER
    # ============================================================

    if not scores:
        return classification_result("general", 0)
    ranking = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    best_type, best_score = ranking[0]

    # Too little evidence
    if best_score < 10:
        return classification_result("general", best_score)

    # If top two are very close, avoid guessing
    if len(ranking) > 1:
        second_score = ranking[1][1]

        if best_score - second_score < 5:
            return classification_result("general", best_score)

    return classification_result(
        best_type,
        best_score
    )