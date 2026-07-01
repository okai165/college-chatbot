import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import pickle
import re

# === Imports from your existing pipeline ===
from app.crawler.pdf_downloader import download_pdf
from app.crawler.gemini_extractor import extract_notification_data
from app.crawler.classifier import classify_notice
from app.db.admission_service import save_admission
from app.db.notice_service import save_notice
from app.db.fee_service import save_fee_structure
from app.crawler.pdf_parser import extract_text_from_pdf, extract_text_from_image
from app.db.scholarship_service import save_scholarship
from app.db.notification_service import save_notification, notification_exists
# ✅ Updated imports from admission_ingest
from app.rag.admission_ingest import save_document, document_exists
from app.crawler.doc_type_mapper import map_doc_type

BASE_URL = "https://www.gcwmaroad.edu.in/"
OUTPUT_DIR = "downloads"
LOG_FILE = "crawl_log.txt"
VISITED_FILE = "visited.pkl"

os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0"}
visited = set()
downloaded_files = []

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
    print(entry)

def save_state():
    with open(VISITED_FILE, "wb") as f:
        pickle.dump(visited, f)

def load_state():
    global visited
    if os.path.exists(VISITED_FILE):
        with open(VISITED_FILE, "rb") as f:
            visited = pickle.load(f)
        log_message(f"Resuming crawl. Already visited {len(visited)} pages.")

def download_pdf_with_retry(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return download_pdf(url)
        except requests.exceptions.RequestException as e:
            log_message(f"Download attempt {attempt+1} failed: {e}")
            time.sleep(delay)
    raise Exception("All download attempts failed")

def process_pdf(title, pdf_url, date=None):
    """Feed discovered PDF into your admissions pipeline."""
    try:
        if document_exists(pdf_url):
            log_message("Already in RAG. Skipping.")
            return False

        file_path = download_pdf_with_retry(pdf_url)

        if pdf_url.lower().endswith((".jpg", ".jpeg", ".png")):
            text = extract_text_from_image(file_path)
        else:
            text = extract_text_from_pdf(file_path)

        if not text.strip():
            log_message("No text extracted")
            return False

        log_message(f"Extracted {len(text)} characters from {os.path.basename(file_path)}")
        preview = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
        log_message(f"Preview: {preview[:200]}...")

        # ✅ Save into unified documents table
        save_document(title=title, date=date, source_url=pdf_url, content=text, doc_type="admission")

        category = classify_notice(title, text)
        log_message(f"CATEGORY: {category}")

        if category == "admission":
            save_admission(title, date, pdf_url, text[:3000])
        elif category == "fee":
            save_fee_structure(title, pdf_url, text[:3000])
        elif category == "scholarship":
            save_scholarship(title, pdf_url, text[:3000])
        else:
            save_notice(title, pdf_url, text[:3000])

        if not notification_exists(pdf_url):
            try:
                data = extract_notification_data(text)
                if data.get("title"):
                    data["source_url"] = pdf_url
                    save_notification(data)
                    log_message("Notification Saved")
            except Exception as gemini_error:
                log_message(f"Gemini skipped: {gemini_error}")

        return True
    except Exception as e:
        log_message(f"Error processing PDF {pdf_url}: {e}")
        return False


def process_html(title, url, soup):
    """Extract text from HTML pages and save into RAG with correct doc_type."""
    try:
        text_chunks = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            text_chunks.append(h.get_text(strip=True))
        for p in soup.find_all("p"):
            text_chunks.append(p.get_text(strip=True))
        for table in soup.find_all("table"):
            text_chunks.append(table.get_text(separator="\n", strip=True))

        content = "\n".join(text_chunks)

        if not content.strip():
            log_message("No text extracted from HTML")
            return False

        log_message(f"Extracted {len(content)} characters from {url}")
        preview = re.sub(r'[^\x20-\x7E\n\r\t]', '', content)
        log_message(f"Preview: {preview[:200]}...")

        # ✅ Use mapper to determine doc_type
        doc_type = map_doc_type(url, title)

        # Save into unified documents table with correct doc_type
        save_document(
            title=title,
            date=None,
            source_url=url,
            content=content,
            doc_type=doc_type
        )

        # ✅ Route to correct service (currently all static pages still use save_notice)
        save_notice(title, url, content[:3000])

        return True

    except Exception as e:
        log_message(f"Error processing HTML {url}: {e}")
        return False

def crawl_page(url):
    if url in visited:
        return
    visited.add(url)
    save_state()

    log_message("="*60)
    log_message(f"CRAWLING: {url}")
    log_message("="*60)

    if url.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
        downloaded_files.append(url)
        log_message(f"Direct file detected: {url}")
        process_pdf(title="Untitled", pdf_url=url)
        return

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        log_message("HEADINGS: " + str(headings[:5]))
        log_message("PARAGRAPHS: " + str(paragraphs[:3]))

        tables = soup.find_all("table")
        log_message(f"TOTAL TABLES: {len(tables)}")
        for i, table in enumerate(tables):
            table_text = table.get_text(separator="\n", strip=True)
            log_message(f"TABLE {i+1} (preview): {table_text[:500]}")

        # ✅ Process HTML content
        process_html(headings[0] if headings else "Untitled", url, soup)

        # Discover and process files
        for link in soup.find_all("a", href=True):
            href = link["href"]
            file_url = urljoin(url, href)
            if href.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
                downloaded_files.append(file_url)
                log_message(f"Found file: {file_url}")
                process_pdf(title=headings[0] if headings else "Untitled", pdf_url=file_url)

        # Recursively follow internal links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            next_url = urljoin(url, href)
            if urlparse(next_url).netloc == urlparse(BASE_URL).netloc:
                if next_url not in visited and next_url.startswith(BASE_URL):
                    crawl_page(next_url)

    except Exception as e:
        log_message(f"Error crawling {url}: {e}")

def write_summary():
    log_message("="*60)
    log_message("UNIFIED CRAWL SUMMARY")
    log_message("="*60)
    log_message(f"Total pages crawled: {len(visited)}")
    log_message(f"Total files discovered: {len(downloaded_files)}")
    log_message("="*60)

if __name__ == "__main__":
    if not os.path.exists(VISITED_FILE):
        open(LOG_FILE, "w").close()
    load_state()

    START_PAGES = [
        BASE_URL,
        BASE_URL + "admissions.php",
        BASE_URL + "module.php?id=52", # About Us
        BASE_URL + "module.php?id=47", # Public Disclosure
        BASE_URL + "module.php?id=53", # Examination Cell
        BASE_URL + "module.php?id=21", # Library
        BASE_URL + "module.php?id=50", # Central Research Laboratory
        BASE_URL + "module.php?id=51", # Innovation and Incubation Centre
        BASE_URL + "module.php?id=54", # Entrepreneurship Cell
        BASE_URL + "module.php?id=48", # Scholarship
        BASE_URL + "module.php?id=49", # Hostel
        BASE_URL + "grievances.php",   # Grievances
        BASE_URL + "module.php?id=40", # NCC
        BASE_URL + "Syllabus/Index/True?pp=UG", # Syllabus
        BASE_URL + "module.php?id=57", # Student Corner
        BASE_URL + "iqac.php",         # IQAC
        BASE_URL + "module.php?id=59", # NIRF
    ]

    for page in START_PAGES:
        crawl_page(page)