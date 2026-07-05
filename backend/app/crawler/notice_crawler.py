import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import pickle

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

def download_file(file_url):
    local_filename = os.path.join(OUTPUT_DIR, os.path.basename(file_url))
    try:
        r = requests.get(file_url, headers=headers, timeout=20)
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            f.write(r.content)
        downloaded_files.append(local_filename)
        log_message(f"Downloaded: {local_filename}")
    except Exception as e:
        log_message(f"Failed to download {file_url}: {e}")

def crawl_page(url):
    if url in visited:
        return
    visited.add(url)
    save_state()

    log_message("="*60)
    log_message(f"CRAWLING: {url}")
    log_message("="*60)

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Log headings and first few paragraphs
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        log_message("HEADINGS: " + str(headings[:5]))
        log_message("PARAGRAPHS: " + str(paragraphs[:3]))

        # NEW: Extract tables
        tables = soup.find_all("table")
        log_message(f"TOTAL TABLES: {len(tables)}")
        for i, table in enumerate(tables):
            table_text = table.get_text(separator="\n", strip=True)
            log_message(f"TABLE {i+1} (preview): {table_text[:500]}")

        # Download linked files
        for link in soup.find_all("a", href=True):
            href = link["href"]
            file_url = urljoin(url, href)
            if href.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
                download_file(file_url)

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
    log_message("CRAWL SUMMARY")
    log_message("="*60)
    log_message(f"Total pages crawled: {len(visited)}")
    log_message(f"Total files downloaded: {len(downloaded_files)}")
    if downloaded_files:
        log_message("Downloaded files list:")
        for f in downloaded_files:
            log_message(f" - {f}")

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
        BASE_URL + "departments.php?id=40", # NCC
        BASE_URL + "Syllabus/Index/True?pp=UG", # Syllabus
        BASE_URL + "module.php?id=57", # Student Corner
        BASE_URL + "iqac.php",         # IQAC
        BASE_URL + "module.php?id=59", # NIRF
    ]

    for page in START_PAGES:
        crawl_page(page)

    write_summary()