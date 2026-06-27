import time
import requests
from app.crawler.admission_api import get_admission_updates
from app.crawler.pdf_downloader import download_pdf
from app.crawler.gemini_extractor import extract_notification_data
from app.crawler.classifier import classify_notice
from app.db.admission_service import save_admission
from app.db.notice_service import save_notice
from app.db.fee_service import save_fee_structure
from app.crawler.pdf_parser import (
    extract_text_from_pdf,
    extract_text_from_image
)
from app.db.scholarship_service import save_scholarship
from app.db.notification_service import (
    save_notification,
    notification_exists
)
from app.rag.admission_ingest import (
    save_admission_document,
    admission_exists
)


def download_pdf_with_retry(url, retries=3, delay=5):
    """Download PDF with retry logic to handle timeouts."""
    for attempt in range(retries):
        try:
            return download_pdf(url)
        except requests.exceptions.RequestException as e:
            print(f"Download attempt {attempt+1} failed: {e}")
            time.sleep(delay)
    raise Exception("All download attempts failed")


def crawl_admissions():
    updates = get_admission_updates()

    total_found = len(updates)
    skipped = 0
    saved = 0
    failed = 0

    print("\n" + "=" * 60)
    print(f"FOUND {total_found} LATEST ADMISSION NOTICES")
    print("=" * 60)

    for notice in updates:
        try:
            title = notice["title"]
            pdf_url = notice["pdf_url"]
            date = notice["date"]

            print("\n================================")
            print("TITLE :", title)
            print("DATE  :", date)
            print("PDF   :", pdf_url)
            print("================================")

            if not pdf_url:
                print("No PDF available. Skipping.")
                skipped += 1
                continue

            if admission_exists(pdf_url):
                print("Already in RAG. Skipping.")
                skipped += 1
                continue

            # Use retry logic for downloads
            file_path = download_pdf_with_retry(pdf_url)

            url_lower = pdf_url.lower()
            if url_lower.endswith((".jpg", ".jpeg", ".png")):
                text = extract_text_from_image(file_path)
            else:
                text = extract_text_from_pdf(file_path)

            if not text.strip():
                print("No text extracted")
                skipped += 1
                continue

            save_admission_document(
                title=title,
                date=date,
                pdf_url=pdf_url,
                content=text
            )

            category = classify_notice(title, text)
            print(f"CATEGORY: {category}")

            if category == "admission":
                save_admission(title, date, pdf_url, text[:3000])
            elif category == "fee":
                save_fee_structure(title, pdf_url, text[:3000])
            elif category == "scholarship":
                save_scholarship(title, pdf_url, text[:3000])
            else:
                save_notice(title, pdf_url, text[:3000])

            saved += 1

            if not notification_exists(pdf_url):
                try:
                    data = extract_notification_data(text)
                    if data.get("title"):
                        data["source_url"] = pdf_url
                        save_notification(data)
                        print("Notification Saved")
                except Exception as gemini_error:
                    print(f"Gemini skipped: {gemini_error}")

        except Exception as e:
            failed += 1
            print(f"Error processing notice: {e}")

    print("\n" + "=" * 60)
    print("ADMISSION CRAWLER FINISHED")
    print("=" * 60)
    print(f"TOTAL FOUND      : {total_found}")
    print(f"NEWLY SAVED      : {saved}")
    print(f"ALREADY SKIPPED  : {skipped}")
    print(f"FAILED           : {failed}")
    print("=" * 60)

    if failed > 0:
        print("PROCESS COMPLETED WITH ERRORS")
    else:
        print("PROCESS COMPLETED SUCCESSFULLY")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    crawl_admissions()
