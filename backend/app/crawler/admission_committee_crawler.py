# import os
# import time
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from datetime import datetime
# import pickle

# # === Imports from your existing pipeline ===
# from app.crawler.pdf_downloader import download_pdf
# from app.crawler.gemini_extractor import extract_notification_data
# from app.crawler.classifier import classify_notice
# from app.db.admission_service import save_admission
# from app.db.notice_service import save_notice
# from app.db.fee_service import save_fee_structure
# from app.crawler.pdf_parser import extract_text_from_pdf, extract_text_from_image
# from app.db.scholarship_service import save_scholarship
# from app.db.notification_service import save_notification, notification_exists
# from app.rag.admission_ingest import save_admission_document, admission_exists

# BASE_URL = "https://www.gcwmaroad.edu.in/"
# OUTPUT_DIR = "downloads"
# LOG_FILE = "crawl_log.txt"
# VISITED_FILE = "visited.pkl"

# os.makedirs(OUTPUT_DIR, exist_ok=True)

# headers = {"User-Agent": "Mozilla/5.0"}
# visited = set()
# downloaded_files = []

# def log_message(message):
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     entry = f"[{timestamp}] {message}"
#     with open(LOG_FILE, "a", encoding="utf-8") as f:
#         f.write(entry + "\n")
#     print(entry)

# def save_state():
#     with open(VISITED_FILE, "wb") as f:
#         pickle.dump(visited, f)

# def load_state():
#     global visited
#     if os.path.exists(VISITED_FILE):
#         with open(VISITED_FILE, "rb") as f:
#             visited = pickle.load(f)
#         log_message(f"Resuming crawl. Already visited {len(visited)} pages.")

# def download_pdf_with_retry(url, retries=3, delay=5):
#     for attempt in range(retries):
#         try:
#             return download_pdf(url)
#         except requests.exceptions.RequestException as e:
#             log_message(f"Download attempt {attempt+1} failed: {e}")
#             time.sleep(delay)
#     raise Exception("All download attempts failed")

# def process_pdf(title, pdf_url, date=None):
#     """Feed discovered PDF into your admissions pipeline."""
#     try:
#         if admission_exists(pdf_url):
#             log_message("Already in RAG. Skipping.")
#             return False

#         file_path = download_pdf_with_retry(pdf_url)

#         url_lower = pdf_url.lower()
#         if url_lower.endswith((".jpg", ".jpeg", ".png")):
#             text = extract_text_from_image(file_path)
#         else:
#             text = extract_text_from_pdf(file_path)

#         if not text.strip():
#             log_message("No text extracted")
#             return False

#         save_admission_document(title=title, date=date, pdf_url=pdf_url, content=text)

#         category = classify_notice(title, text)
#         log_message(f"CATEGORY: {category}")

#         if category == "admission":
#             save_admission(title, date, pdf_url, text[:3000])
#         elif category == "fee":
#             save_fee_structure(title, pdf_url, text[:3000])
#         elif category == "scholarship":
#             save_scholarship(title, pdf_url, text[:3000])
#         else:
#             save_notice(title, pdf_url, text[:3000])

#         if not notification_exists(pdf_url):
#             try:
#                 data = extract_notification_data(text)
#                 if data.get("title"):
#                     data["source_url"] = pdf_url
#                     save_notification(data)
#                     log_message("Notification Saved")
#             except Exception as gemini_error:
#                 log_message(f"Gemini skipped: {gemini_error}")

#         return True
#     except Exception as e:
#         log_message(f"Error processing PDF {pdf_url}: {e}")
#         return False

# def crawl_page(url):
#     if url in visited:
#         return
#     visited.add(url)
#     save_state()

#     log_message("="*60)
#     log_message(f"CRAWLING: {url}")
#     log_message("="*60)

#     try:
#         response = requests.get(url, headers=headers, timeout=20)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")

#         headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])]
#         paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
#         log_message("HEADINGS: " + str(headings[:5]))
#         log_message("PARAGRAPHS: " + str(paragraphs[:3]))

#         tables = soup.find_all("table")
#         log_message(f"TOTAL TABLES: {len(tables)}")
#         for i, table in enumerate(tables):
#             table_text = table.get_text(separator="\n", strip=True)
#             log_message(f"TABLE {i+1} (preview): {table_text[:500]}")

#         # Discover and process PDFs
#         for link in soup.find_all("a", href=True):
#             href = link["href"]
#             file_url = urljoin(url, href)
#             if href.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
#                 downloaded_files.append(file_url)
#                 log_message(f"Found file: {file_url}")
#                 process_pdf(title=headings[0] if headings else "Untitled", pdf_url=file_url)

#         # Recursively follow internal links
#         for link in soup.find_all("a", href=True):
#             href = link["href"]
#             next_url = urljoin(url, href)
#             if urlparse(next_url).netloc == urlparse(BASE_URL).netloc:
#                 if next_url not in visited and next_url.startswith(BASE_URL):
#                     crawl_page(next_url)

#     except Exception as e:
#         log_message(f"Error crawling {url}: {e}")

# def write_summary():
#     log_message("="*60)
#     log_message("UNIFIED CRAWL SUMMARY")
#     log_message("="*60)
#     log_message(f"Total pages crawled: {len(visited)}")
#     log_message(f"Total files discovered: {len(downloaded_files)}")
#     log_message("="*60)

# if __name__ == "__main__":
#     if not os.path.exists(VISITED_FILE):
#         open(LOG_FILE, "w").close()
#     load_state()

#     START_PAGES = [
#         BASE_URL,
#         BASE_URL + "admissions.php",
#         BASE_URL + "aboutus.php",
#         BASE_URL + "public_disclosure.php",
#         BASE_URL + "academics.php",
#         BASE_URL + "research.php",
#         BASE_URL + "entrepreneurship.php",
#         BASE_URL + "student_corner.php",
#         BASE_URL + "iqac.php",
#         BASE_URL + "nirf.php",
#         BASE_URL + "login.php"
#     ]

#     for page in START_PAGES:
#         crawl_page(page)

#     write_summary()