import re

IGNORE_LINES = [
    "government college",
    "cluster university",
    "university of",
    "directorate of colleges",
    "office of the principal",
    "m.a. road",
    "srinagar",
    "naac",
    "ugc",
    "website",
    "email",
    "phone",
    "contact",
    "www.",
    "http",
    "https",
    "page",
    "©",
]

KEYWORDS = {
    "admission": 12,
    "notification": 10,
    "notice": 10,
    "selection list": 12,
    "merit list": 12,
    "provisional": 8,
    "final": 6,
    "fee": 10,
    "fee structure": 12,
    "eligibility": 10,
    "scholarship": 10,
    "examination": 10,
    "exam": 10,
    "date sheet": 10,
    "schedule": 8,
    "time table": 8,
    "timetable": 8,
    "calendar": 8,
    "syllabus": 8,
    "hostel": 8,
    "library": 8,
    "research": 8,
    "iqac": 8,
    "nirf": 8,
    "aqar": 8,
    "committee": 6,
    "grievance": 8,
    "principal": 6,
    "vac": 5,
    "aec": 5,
    "sec": 5,
    "major": 4,
    "minor": 4,
}


BAD_STARTS = (
    "the ",
    "this ",
    "candidates ",
    "students ",
    "all students ",
    "applications ",
    "it is ",
    "these ",
    "those ",
)


def normalize(line: str):
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def is_junk(line: str):

    if not line:
        return True

    lower = line.lower()

    if len(lower) < 5:
        return True

    if len(lower) > 120:
        return True

    if any(x in lower for x in IGNORE_LINES):
        return True

    if re.fullmatch(r"[\d\s\-_/]+", lower):
        return True

    if re.search(r"page\s+\d+", lower):
        return True

    if lower.startswith(BAD_STARTS):
        return True

    digits = len(re.findall(r"\d", line))

    if digits > len(line) * 0.45:
        return True

    return False


def score(candidate: str, line_no: int):

    s = 0

    lower = candidate.lower()

    # Top of document
    if line_no < 8:
        s += 6

    elif line_no < 15:
        s += 3

    # Length
    words = len(candidate.split())

    if 2 <= words <= 10:
        s += 4

    elif words <= 16:
        s += 2

    # Year
    if re.search(r"\b20\d{2}\b", candidate):
        s += 5

    # ALL CAPS
    letters = re.sub(r"[^A-Za-z]", "", candidate)

    if letters and letters.isupper():
        s += 4

    # Title Case
    if candidate == candidate.title():
        s += 2

    # Keywords
    for k, w in KEYWORDS.items():
        if k in lower:
            s += w

    # Structured
    if ":" in candidate or "-" in candidate:
        s += 2

    return s


def extract_pdf_title(text: str, fallback_title=None):

    if not text:
        return fallback_title or "Untitled", 0

    # Only inspect first page / beginning
    text = text[:3000]

    lines = []

    for raw in text.splitlines():

        raw = normalize(raw)

        if is_junk(raw):
            continue

        lines.append(raw)

    candidates = []

    for i, line in enumerate(lines[:20]):

        candidates.append((line, i))

        # merge with next line

        if i + 1 < len(lines):

            merged = f"{line} - {lines[i+1]}"

            if len(merged) < 120:

                candidates.append((merged, i))

        # merge three lines

        if i + 2 < len(lines):

            merged = f"{line} - {lines[i+1]} - {lines[i+2]}"

            if len(merged) < 120:

                candidates.append((merged, i))

    best = None

    best_score = -1

    for candidate, line_no in candidates:

        sc = score(candidate, line_no)

        if sc > best_score:

            best_score = sc

            best = candidate

    if best:

        best = re.sub(r"\s+", " ", best).strip(" -:|")

        return best, best_score

    if fallback_title:

        return fallback_title, 0

    return "Untitled", 0