import os
import re

from app.services.llm import generate_llm_response


GENERIC_TITLES = {
    "admissions",
    "admission",
    "admissions 2026",
    "admissions 2025",
    "notice",
    "notification",
    "circular",
    "document",
    "college notice",
}

BAD_LINES = [
    "government of",
    "government college",
    "government college for women",
    "constituent college",
    "cluster university",
    "higher education department",
    "directorate of colleges",
    "naac",
    "estd",
    "m.a road",
    "srinagar",
    "www.",
    "http",
    "page ",
    "programme/ course",
    "programme",
    "department",
    "course type",
    "eligibility",
    "s no",
    "intake",
    "major",
    "minor",
    "total fee",
]


def _clean(line: str):
    line = re.sub(r"\s+", " ", line).strip(" -:\t")
    return line


def _looks_like_title(line: str):
    line = _clean(line)

    if len(line) < 8:
        return False

    if len(line) > 140:
        return False

    lower = line.lower()

    if lower in GENERIC_TITLES:
        return False

    for bad in BAD_LINES:
        if bad in lower:
            return False

    return True


def extract_document_title(
    text: str,
    fallback_title: str = "Untitled",
    filename: str | None = None,
):
    lines = [_clean(x) for x in text.splitlines()[:40]]

    # =====================================================
    # 1. Look for Subject / Sub
    # =====================================================
    for i, line in enumerate(lines):
        lower = line.lower()

        if lower.startswith("subject") or lower.startswith("sub"):
            # Same line
            parts = line.split(":", 1)
            if len(parts) == 2 and _looks_like_title(parts[1]):
                return parts[1].strip()

            # Next few lines
            for j in range(i + 1, min(i + 4, len(lines))):
                if _looks_like_title(lines[j]):
                    return lines[j]

    # =====================================================
    # 2. Skip institutional heading and find first real title
    # =====================================================
    for line in lines:
        if _looks_like_title(line):
            return line

    # =====================================================
    # 3. Ask the LLM
    # =====================================================
    prompt = f"""
Extract ONLY the official document title.

Rules:
- Return the exact title written in the document.
- Ignore the issuing authority.
- Ignore college name.
- Ignore addresses.
- Ignore table headings.
- Ignore 'Government of...' unless it is actually the title.
- Ignore 'Programme', 'Department', 'Eligibility', etc.
- If there is a Subject line, use that.
- Maximum 12 words.
- Return ONLY the title.
- If no title exists return NONE.

Document:

{text[:3500]}
"""

    try:
        title = generate_llm_response(prompt).strip()

        print("LLM TITLE:", title)

        cleaned = title.lower().strip()

        if (
            cleaned
            and cleaned != "none"
            and cleaned not in GENERIC_TITLES
            and len(title) > 6
        ):
            return title

    except Exception as e:
        print("TITLE ERROR:", e)

    # =====================================================
    # 4. Filename fallback
    # =====================================================
    if filename:
        return (
            os.path.splitext(filename)[0]
            .replace("_", " ")
            .replace("-", " ")
        )

    return fallback_title