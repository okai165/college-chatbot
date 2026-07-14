import re

BAD_PATTERNS = [
    "pass out",
    "major/minor",
    "s.no",
    "credit",
    "code",
    "table",
]

IGNORE_HEADERS = [
    "government of jammu and kashmir",
    "directorate of colleges",
    "government college for women",
    "constituent college of cluster university",
    "office of the principal",
    "m.a. road",
    "naac",
    "ugc",
    "estd",
]

GENERIC_TITLES = {
    "notice",
    "notification",
    "circular",
    "important",
    "information",
    "about",
    "about us",
    "overview",
    "home",
    "gallery",
}

TITLE_KEYWORDS = {
    "admission": 15,
    "notification": 12,
    "selection list": 12,
    "merit list": 12,

    "fee": 10,
    "exam": 10,
    "examination": 10,
    "schedule": 10,
    "timetable": 10,
    "time table": 10,
    "date sheet": 10,

    "scholarship": 10,

    "library": 9,
    "research": 9,
    "innovation": 9,
    "hostel": 9,
    "grievance": 9,
    "iqac": 9,
    "nirf": 9,
    "aqar": 9,

    "department": 8,
    "faculty": 8,
    "committee": 8,
    "principal": 8,
    "contact": 8,
    "syllabus": 8,

    "cell": 6,
    "centre": 6,
    "center": 6,
    "laboratory": 6,
    "course": 6,
}


def clean_title(title: str):
    title = re.sub(r"\s+", " ", title).strip()

    title = re.sub(
        r"\s*\|\s*govt\.?.*$",
        "",
        title,
        flags=re.I,
    )

    title = re.sub(
        r"\s*[-–]\s*govt\.?.*$",
        "",
        title,
        flags=re.I,
    )

    return title.strip()


def score_title(title: str):

    if not title:
        return -100

    title = clean_title(title)

    if len(title) < 8 or len(title) > 120:
        return -100

    lower = title.lower()

    if lower in GENERIC_TITLES:
        return -100

    if any(header in lower for header in IGNORE_HEADERS):
        return -100

    if any(pattern in lower for pattern in BAD_PATTERNS):
        return -100

    if re.search(r"\b(page\s*\d+|row\s*\d+)\b", lower):
        return -100

    score = 0

    words = len(title.split())

    if 3 <= words <= 10:
        score += 4

    elif 11 <= words <= 16:
        score += 2

    if title.isupper():
        score += 2

    if ":" in title:
        score += 2

    if "-" in title:
        score += 1

    if re.search(r"\b20\d{2}\b", title):
        score += 5

    if re.search(r"\b202\d[-/]\d{2}\b", title):
        score += 6

    for keyword, weight in TITLE_KEYWORDS.items():
        if keyword in lower:
            score += weight

    # Penalize vague "About ..." headings
    if lower.startswith("about "):

        score -= 5

        # Unless it identifies something specific
        if any(x in lower for x in [
            "library",
            "examination",
            "scholarship",
            "hostel",
            "iqac",
            "cell",
            "committee",
            "research",
            "innovation",
            "laboratory",
        ]):
            score += 6

    return score


def extract_best_title(text: str, html_title=None):

    candidates = []

    if html_title:
        candidates.append(clean_title(html_title))

    lines = text.splitlines()

    for line in lines[:50]:

        line = clean_title(line)

        if len(line) < 8:
            continue

        if len(line) > 120:
            continue

        lower = line.lower()

        if lower in GENERIC_TITLES:
            continue

        if any(header in lower for header in IGNORE_HEADERS):
            continue

        if re.search(
            r"\b(table|eligibility|intake|s\.?no|roll no|credits?)\b",
            lower,
        ):
            continue

        digits = len(re.findall(r"\d", line))
        if digits > len(line) * 0.4:
            continue

        candidates.append(line)

    best = None
    best_score = -100

    for candidate in dict.fromkeys(candidates):   # remove duplicates
        score = score_title(candidate)

        if score > best_score:
            best = candidate
            best_score = score

    return best if best else "Untitled"