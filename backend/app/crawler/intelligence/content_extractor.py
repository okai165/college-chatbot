from bs4 import BeautifulSoup
import re


# =========================
# CLEANING CORE
# =========================

def clean_dom(soup: BeautifulSoup):
    """
    Remove obvious noise elements before extraction
    """
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form", "aside"]):
        tag.decompose()
    return soup


def extract_text_dom(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    soup = clean_dom(soup)

    text = soup.get_text(separator="\n", strip=True)

    lines = [
        line.strip()
        for line in text.splitlines()
        if len(line.strip()) > 3
    ]

    return "\n".join(lines)


# =========================
# CONTENT VALIDATION
# =========================

def is_valid_content(text: str) -> bool:
    if not text:
        return False

    text_len = len(text)

    # allow real CMS pages, block only truly empty pages
    if text_len < 120:
        return False

    lower = text.lower()

    junk_signals = [
        "enable javascript",
        "javascript required",
        "cookie",
        "404",
        "not found",
        "access denied",
        "page not found"
    ]

    if any(j in lower for j in junk_signals):
        return False

    return True


# =========================
# MAIN EXTRACTOR
# =========================

def extract_main_content(html: str) -> str:
    """
    Primary extractor used by crawler
    """

    raw_text = extract_text_dom(html)

    if is_valid_content(raw_text):
        return raw_text

    return ""


# =========================
# PAGE QUALITY CHECK
# =========================

def is_real_page(soup: BeautifulSoup) -> bool:
    """
    Decides whether page should be processed at all
    (NOT too strict — CMS-safe)
    """

    text = soup.get_text(separator=" ", strip=True)
    links = soup.find_all("a")

    text_len = len(text)
    link_count = len(links)

    # too empty → reject
    if text_len < 80:
        return False

    lower = text.lower()

    junk_signals = [
        "enable javascript",
        "cookie",
        "404",
        "not found",
        "error",
        "access denied"
    ]

    if any(j in lower for j in junk_signals):
        return False

    # reject extreme menu-only shells
    if text_len < 200 and link_count > 80:
        return False

    return True