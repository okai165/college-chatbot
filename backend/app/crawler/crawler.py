import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re

# ======================
# PIPELINE IMPORTS
# ======================
from app.crawler.pdf_downloader import download_pdf
from app.crawler.frontier import URLFrontier
from app.db.admission_service import save_admission
from app.db.notice_service import save_notice
from app.db.fee_service import save_fee_structure
from app.crawler.pdf_parser import extract_text_from_pdf, extract_text_from_image
from app.db.scholarship_service import save_scholarship
from app.db.notification_service import save_notification, notification_exists
from app.rag.admission_ingest import save_document, document_exists
from app.crawler.doc_type_mapper import map_doc_type
from app.crawler.intelligence.content_extractor import extract_main_content, is_real_page
from app.crawler.intelligence.fetcher import fetch_html
from app.crawler.url_normalizer import normalize_url
from app.crawler.intelligence.llm_cleaner import clean_text_llm
from app.crawler.title_extractor import extract_document_title
from app.crawler.gemini_extractor import extract_notification_data
from app.services.quick_link_service import save_quick_link
from app.crawler.dynamic_module_crawler import fetch_department_profile
from app.crawler.dynamic_module_crawler import load_dynamic_content
from app.crawler.intelligence.pdf_title_extractor import extract_pdf_title
from app.crawler.intelligence.title_ranker import (
    extract_best_title,
    score_title,
)
from app.db.admission_service import save_admission
from app.db.activity_schedule_service import save_activity_schedule
from app.db.eligibility_service import save_eligibility
# ✅ NEW: Persistent state store
from app.crawler.state_store import init_db, is_visited, mark_visited

# ======================
# CONFIG
# ======================
BASE_URL = "https://www.gcwmaroad.edu.in/"
LOG_FILE = "crawl_log.txt"

headers = {"User-Agent": "Mozilla/5.0"}

os.makedirs("downloads", exist_ok=True)


# ======================
# LOGGING
# ======================
def log_message(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def chunk_text(text, chunk_size=400, overlap=80):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start += chunk_size - overlap

    return chunks
# ======================
# DOWNLOAD
# ======================
def download_pdf_with_retry(url, retries=3):
    for i in range(retries):
        try:
            return download_pdf(url)
        except Exception as e:
            log_message(f"Retry {i+1} failed: {e}")
            time.sleep(3)
    raise Exception("Download failed")


# ======================
# PDF PROCESSING
# ======================
def process_pdf(title, pdf_url, date=None, parent_url=None):
    try:
        pdf_url = normalize_url(pdf_url)
        if document_exists(pdf_url):
            log_message("Already in RAG. Skipping.")
            return False

        file_path = download_pdf_with_retry(pdf_url)

        if pdf_url.lower().endswith((".jpg", ".jpeg", ".png")):
            text = extract_text_from_image(file_path)
        else:
            text = extract_text_from_pdf(file_path)

        if not text.strip():
            return False

        filename = os.path.basename(urlparse(pdf_url).path)
        original_title = title

        # ======================
        # TITLE PIPELINE
        # ======================
        # ======================
        # TITLE PIPELINE (FIXED)
        # ======================

        base_title = original_title or filename

        def is_safe_llm_title(t):
            if not t:
                return False
            t = t.lower()

            # reject entity-style outputs
            if t.startswith("institute name"):
                return False

            # reject overly generic or noisy outputs
            if len(t) > 120:
                return False

            # avoid wrong semantic overwrites for reports
            if "govt" in t and "nirf" not in t:
                return False

            return True


        rule_title, confidence = extract_pdf_title(
            text,
            base_title
        )

        if confidence >= 20:
            title_candidate = rule_title
            llm_title = None
        else:
            llm_title = extract_document_title(
                text=text[:2500],
                fallback_title=base_title,
                filename=filename
            )

            if is_safe_llm_title(llm_title):
                title_candidate = llm_title
            else:
                title_candidate = rule_title


        # Step 2: ranker only refines (NOT overwrite blindly)
        candidate_score = score_title(title_candidate)

        ranked_title = extract_best_title(text, title_candidate)

        if ranked_title:
            ranked_score = score_title(ranked_title)
        else:
            ranked_score = 0

        print(f"Candidate : {title_candidate} ({candidate_score})")
        print(f"Ranked    : {ranked_title} ({ranked_score})")

        if (
            ranked_title
            and ranked_score > candidate_score
            and ranked_title.lower() != title_candidate.lower()
        ):
            title = ranked_title
        else:
            title = title_candidate

        # cleanup
        title = re.sub(r"\s+", " ", title).strip(" -:|")
        print("=" * 60)
        print("Filename :", filename)
        print("Fallback :", original_title)
        print("LLM Title:", llm_title)
        print("Final    :", title)
        print("=" * 60)

        log_message(f"Extracted {len(text)} chars from {filename}")

        # ======================
        # SAFE LLM CLEANING
        # ======================
        try:
            lower_text = text.lower()
            if "<html" in lower_text and ("gateway" in lower_text or "timeout" in lower_text):
                log_message("Skipping LLM cleaner (bad HTML error response)")
            else:
                cleaned = clean_text_llm(text)
                if cleaned and isinstance(cleaned, str) and len(cleaned.strip()) > 200:
                    text = cleaned
        except Exception as e:
            log_message(f"LLM cleaning skipped: {e}")

        classification = map_doc_type(
            pdf_url,
            title,
            text
        )

        doc_type = classification["type"]
        confidence = classification["confidence"]
        score = classification["score"]

        log_message(
            f"""
        DOCUMENT CLASSIFICATION

        Title      : {title}
        Type       : {doc_type}
        Score      : {score}
        Confidence : {confidence}
        """
        )
        # CHECK ONCE BEFORE ANY PROCESSING
        # if document_exists(pdf_url):
        #     log_message("Already in RAG. Skipping full document.")
        #     return False

        chunks = chunk_text(text, chunk_size=400, overlap=80)

        for i, chunk in enumerate(chunks, start=1):
            save_document(
                title=f"{title} (chunk {i})",
                date=date,
                source_url=pdf_url,
                content=chunk,
                doc_type=doc_type
            )   

        category =doc_type
        log_message(f"CATEGORY: {category}")

        if category == "admission":
            save_admission(title, date, pdf_url, text[:3000])
        elif category == "fee":
            save_fee_structure(title, pdf_url, text[:3000])
        elif category == "scholarship":
            save_scholarship(title, pdf_url, text[:3000])
        elif category == "notice":
            save_notice(
                title,
                pdf_url,
                text[:3000]
            )

        if not notification_exists(pdf_url):
            try:
                data = extract_notification_data(text)
                if data.get("title"):
                    data["source_url"] = pdf_url
                    save_notification(data)
                    log_message("Notification saved")
            except Exception as e:
                log_message(f"Notification skipped: {e}")

        return True

    except Exception as e:
        log_message(f"PDF error {pdf_url}: {e}")
        return False


# ======================
# HTML PROCESSING
# ======================
def process_html(title, url, soup, date=None):
    try:
        url = normalize_url(url)
        if not is_real_page(soup):
            log_message("Detected empty shell page → skipping HTML ingestion")
            return False

        html = str(soup)
        content = extract_main_content(html)

        # -----------------------------------------
        # Dynamic page extraction (modules + departments)
        # -----------------------------------------
        try:

            dynamic = load_dynamic_content(html)

            if dynamic:

                title = dynamic["title"]
                content = dynamic["content"]

                log_message(
                    f"Loaded dynamic content ({len(content)} chars)"
                )

        except Exception as e:
            log_message(f"Dynamic extraction failed: {e}")
        print("=" * 80)
        print("URL:", url)
        print("TITLE:", title)
        print("EXTRACTED CONTENT:")
        print(content)
        print("=" * 80)
        fallback = "\n".join(
            [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])] +
            [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        )

        if len(content.strip()) < 300:
            content = fallback
        content = re.sub(r"\r", "", content)

        meaningful_lines = [
            line.strip()
            for line in content.split("\n")
            if len(line.strip()) > 25
        ]

        content = re.sub(r"\s+", " ", content).strip()

        print("Length:", len(content))
        print("Meaningful lines:", len(meaningful_lines))

        if len(content) < 10:

            fallback = "\n".join(

                [
                    h.get_text(" ", strip=True)
                    for h in soup.find_all(["h1","h2","h3"])
                ]
                +
                [
                    p.get_text(" ", strip=True)
                    for p in soup.find_all("p")
                ]
            )

            if len(fallback) > 120:
                content = fallback
            else:
                log_message("Skipping tiny HTML page")
                return False
        if content.strip().lower() == "gallery":
            log_message("Skipping gallery page")
            return False
        #if len(content) < 150:
         #   log_message("HTML content too small → skipping")
          #  return False

        # ---------- Better title extraction ----------
        if not title or len(title.strip()) < 3:
            if soup.title and soup.title.string:
                title = soup.title.string.strip()

        title = re.sub(r"\s+", " ", title).strip()

        BAD_TITLES = {
            "",
            "home",
            "index",
            "index.php",
            "default",
            "welcome",
            "module.php",
            "government college for women",
            "gcw",
            "gallery",
        }
        clean_title = re.sub(r"\s+", " ", title).strip().lower()
        navigation_words = [
            "gallery",
            "faculty profile",
            "notice board",
            "photo gallery",
        ]

        hits = sum(word in content.lower() for word in navigation_words)

        if hits >= 2 and len(content) < 500:
            log_message("Navigation page detected")
            return False
        if (
            not clean_title
            or clean_title in BAD_TITLES
            or clean_title.endswith(".php")
            or len(clean_title) < 3
        ):
            log_message(f"Skipping HTML page because title is invalid: '{title}'")
            return False

        classification = map_doc_type(
            url,
            title,
            content
        )

        doc_type = classification["type"]
        confidence = classification["confidence"]
        score = classification["score"]

        log_message(
            f"""
        DOCUMENT CLASSIFICATION

        Title      : {title}
        Type       : {doc_type}
        Score      : {score}
        Confidence : {confidence}
        """
        )
        SPECIAL_PAGES = {
            "student login": [
                "student login",
                "login"
            ],
            "Know your Roll No": [
                "know your roll no",
                "know your roll number",
                "roll number"
            ],
            "Know your Time Table": [
                "know your timetable",
                "know your time table",
                "time table",
                "timetable",
                "schedule"
            ]
        }

        page = (title + " " + content).lower()

        for page_title, keywords in SPECIAL_PAGES.items():
            if any(keyword in page for keyword in keywords):

                save_quick_link(
                    title=page_title,
                    url=url,
                    keywords=keywords,
                    description=page_title,
                )

                log_message(f"Saved quick link: {page_title}")

                break
        
        if doc_type == "admission":
            save_admission(title, date, url, content[:3000])

        elif doc_type == "activity_schedule":
            save_activity_schedule(title, date, url, content[:3000])

        elif doc_type == "fee":
            save_fee_structure(title, url, content[:3000])

        elif doc_type == "eligibility":
            
            save_eligibility(title, date, url, content[:3000])

        elif doc_type == "scholarship":
            save_scholarship(title, url, content[:3000])

        elif doc_type == "notice":
            save_notice(title, url, content[:3000])
    
        save_document(
            title=title,
            date=None,
            source_url=url,
            content=content,
            doc_type=doc_type
        )

        # if doc_type == "notice":
        #     save_notice(
        #         title,
        #         url,
        #         content[:3000]
        #     )

        return True

    except Exception as e:
        log_message(f"HTML error {url}: {e}")
        return False
    
#--------------------------#
#--------------------------#
# pdf title
# -------------------------#
# -------------------------#    
def get_pdf_title(link, file_url):
    text = link.get_text(" ", strip=True)

    GENERIC = {
        "", "click here", "download", "pdf", "view",
        "details", "read more", "admissions 2026", "admission 2026"
    }

    if text.lower() in GENERIC:
        return os.path.basename(urlparse(file_url).path)

    return text

# ======================
# CRAWLER
# ======================
def crawl_page(url, frontier):
    url = url = normalize_url(url)

    # Skip if already crawled successfully
    if is_visited(url):
        return

    log_message("=" * 60)
    log_message(f"CRAWLING: {url}")
    success = False

    try:
        # -------------------------------
        # Handle document URLs
        # -------------------------------
        if url.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):

            success = process_pdf(
                os.path.basename(url),
                url
            )

            if success:
                mark_visited(url)
                log_message(f"PDF completed: {url}")
            else:
                log_message(f"PDF failed, retry later: {url}")

            return

        # -------------------------------
        # Fetch HTML
        # -------------------------------
        html = fetch_html(url)

        if not html:
            log_message("Empty response → skipping")
            return


        soup = BeautifulSoup(html, "html.parser")
        print("\n" + "=" * 80)
        print("URL:", url)

        print("\nHTML <title>:")
        print(soup.title.get_text(strip=True) if soup.title else "None")

        print("\nH1 / H2 / H3 Tags:")

        for tag in soup.find_all(["h1", "h2", "h3"]):
            print(f"{tag.name}: {tag.get_text(' ', strip=True)}")

        print("=" * 80 + "\n")

        raw_text = extract_main_content(html)

        print("=" * 60)
        print(raw_text[:1200])
        print("=" * 60)

        # Default title from <title>
        candidate_title = ""
        if soup.title:
            candidate_title = soup.title.get_text(" ", strip=True)

        # Prefer H1 if it is better
        h1 = soup.find("h1")
        if h1:
            h1_title = h1.get_text(" ", strip=True)

            if (
                h1_title
                and score_title(h1_title) >= score_title(candidate_title)
            ):
                candidate_title = h1_title

        # Final title
        title = candidate_title or os.path.basename(url)

        print("Final HTML Title:", title)

        success=process_html(title, url, soup, datetime.now())

        if success:
            mark_visited(url)
            log_message(f"Marked visited after successful ingestion: {url}")
        else:
            log_message(f"Ingestion failed, will retry later: {url}")

        # -------------------------------
        # Discover new URLs
        # -------------------------------
        for a in soup.find_all("a", href=True):

            next_url = normalize_url(
                urljoin(url, a["href"])
            )

            if urlparse(next_url).netloc != urlparse(BASE_URL).netloc:
                continue

            if not is_visited(next_url):
                frontier.add(next_url)

    except Exception as e:
        log_message(f"Crawl error {url}: {e}")


# ======================
# MAIN
# ======================
if __name__ == "__main__":
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
    init_db()

    START_PAGES = [
        BASE_URL,
        #BASE_URL + "admissions.php",
        BASE_URL + "module.php?id=52",
        #BASE_URL + "module.php?id=47",
        #BASE_URL + "module.php?id=53",
        #BASE_URL + "module.php?id=21",
        #BASE_URL + "module.php?id=50",
        #BASE_URL + "module.php?id=51",
        #BASE_URL + "module.php?id=54",
        #BASE_URL + "module.php?id=48",
        #BASE_URL + "module.php?id=49",
        #BASE_URL + "grievances.php",
        #BASE_URL + "departments.php?id=40",
        #BASE_URL + "Syllabus/Index/True?pp=UG",
        #BASE_URL + "module.php?id=57",
        #BASE_URL + "iqac.php",
        #BASE_URL + "module.php?id=59",
    ]

    frontier = URLFrontier()

    for page in START_PAGES:
        frontier.add(normalize_url(page))

    while not frontier.empty():

        url = frontier.pop()

        crawl_page(url, frontier)