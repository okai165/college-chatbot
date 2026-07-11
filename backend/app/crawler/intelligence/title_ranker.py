import re

BAD_PATTERNS = [
    "eligibility",
    "programme",
    "program",
    "course",
    "pass out",
    "intake",
    "major/minor",
    "s.no",
    "table",
    "semester",
    "syllabus",
    "credit",
    "subject",
    "marks",
    "code",
    "section",
]


def score_title(t: str) -> int:
    if not t:
        return 0

    t = re.sub(r"\s+", " ", t).strip()

    # hard constraints
    if len(t) < 10 or len(t) > 120:
        return 0

    low = t.lower()

    # reject noisy patterns
    if any(b in low for b in BAD_PATTERNS):
        return 0

    # reject table-like noise
    if re.search(r"\b(\d+\s*/\s*\d+|page\s*\d+|row\s*\d+)\b", low):
        return 0

    score = 0

    # strong structural signal
    if t.isupper():
        score += 4

    # title-like keywords
    title_keywords = {
    "admission",
    "notice",
    "circular",
    "result",
    "fee",
    "schedule",
    "exam",
    "department",
    "principal",
    "faculty",
    "grievance",
    "library",
    "hostel",
    "committee",
    "iqac",
    "nirf",
    "aqar",
    "scholarship",
    "placement",
    "syllabus",
    "timetable",
    "calendar",
    "research",
    "contact",
    }
    if any(word in low for word in title_keywords):
        score += 8

    # boost meaningful length (not too short, not too long)
    word_count = len(t.split())
    if 4 <= word_count <= 12:
        score += 2

    return score


def extract_best_title(text: str, title: str = None):
    candidates = []

    # 1. safe fallback first
    if title:
        candidates.append(title)

    # 2. scan only structured early content (not raw spam lines)
    lines = text.split("\n")

    for l in lines[:40]:
        l = re.sub(r"\s+", " ", l).strip()

        if len(l) < 10:
            continue

        if len(l) > 120:
            continue

        # skip obvious noise
        if re.search(r"\b(table|eligibility|course|department|intake|s\.no)\b", l.lower()):
            continue

        # skip numeric-heavy lines (tables)
        if len(re.findall(r"\d", l)) > 6:
            continue

        candidates.append(l)

    best = None
    best_score = 0

    for c in candidates:
        s = score_title(c)
        if s > best_score:
            best = c
            best_score = s

    return best or title