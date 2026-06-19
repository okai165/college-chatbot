import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.crawler.pdf_downloader import download_pdf
from app.crawler.pdf_parser import extract_text
from app.crawler.gemini_extractor import extract_notification_data

from app.db.notification_service import (
    save_notification,
    notification_exists
)
from app.rag.admission_ingest import save_admission_document
def crawl_admissions():

    url = "https://www.gcwmaroad.edu.in/admissions.php"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    processed_urls = set()

    print("\nPDF LINKS FOUND:\n")

    for link in soup.find_all("a"):

        href = link.get("href")

        if not href:
            continue

        if ".pdf" not in href.lower():
            continue

        pdf_url = urljoin(url, href)

        # Skip duplicate links
        if pdf_url in processed_urls:
            continue

        processed_urls.add(pdf_url)

        # Skip NIRF reports
        filename = pdf_url.lower()

        if "nirf" in filename:
            print(f"Skipping NIRF Report: {pdf_url}")
            continue

        try:

            print(f"\nProcessing: {pdf_url}")

            # Skip if already saved
            if notification_exists(pdf_url):
                print("Already processed. Skipping Gemini.")
                continue

        
            pdf_path = download_pdf(pdf_url)

            text = extract_text(pdf_path)

            if not text.strip():

                print("No text extracted")
                continue
            
            title = link.get_text(strip=True)
            print("CALLING SAVE_ADMISSION_DOCUMENT")
            save_admission_document(
                title=title,
                date="",
                pdf_url=pdf_url,
                content=text
            )

            if notification_exists(pdf_url):
                print("Notification already exists. Skipping Gemini.")
                continue

            print("Sending to Gemini...")

            data = extract_notification_data(text)


            print("Gemini Response Received")

            print(data)

            if not data.get("title"):
                print("Skipping Empty Notification")
                continue

            # Skip empty responses
            if not data.get("title"):
                print("Skipping empty Gemini result")
                continue

            data["source_url"] = pdf_url

            print("Saving to Database...")

            save_notification(data)

            print(
                f"Saved Notification: {data['title']}"
            )

        except Exception as e:

            print(
                f"Error processing {pdf_url}: {e}"
            )

            continue


if __name__ == "__main__":
    crawl_admissions()