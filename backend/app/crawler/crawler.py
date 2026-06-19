from app.crawler.admission_api import get_admission_updates
from app.crawler.pdf_downloader import download_pdf
from app.crawler.pdf_parser import extract_text
from app.crawler.gemini_extractor import extract_notification_data

from app.db.notification_service import (
    save_notification,
    notification_exists
)

from app.rag.admission_ingest import (
    save_admission_document
)


def crawl_admissions():

    updates = get_admission_updates()

    print(
        f"\nFOUND {len(updates)} ADMISSION NOTICES\n"
    )

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

            # Skip notices without PDF
            if not pdf_url:

                print(
                    "No PDF available. Skipping."
                )

                continue

            # Download PDF
            pdf_path = download_pdf(pdf_url)

            # Extract PDF text
            text = extract_text(pdf_path)

            if not text.strip():

                print(
                    "No text extracted"
                )

                continue

            print(
                "CALLING SAVE_ADMISSION_DOCUMENT"
            )

            # Save to RAG documents table
            save_admission_document(
                title=title,
                date=date,
                pdf_url=pdf_url,
                content=text
            )

            # Skip Gemini if already saved
            if notification_exists(pdf_url):

                print(
                    "Notification already exists. Skipping Gemini."
                )

                continue

            print(
                "Sending to Gemini..."
            )

            data = extract_notification_data(text)

            print(
                "Gemini Response Received"
            )

            if not data.get("title"):

                print(
                    "Skipping Empty Notification"
                )

                continue

            data["source_url"] = pdf_url

            print(
                "Saving Notification..."
            )

            save_notification(data)

            print(
                f"Saved Notification: {data['title']}"
            )

        except Exception as e:

            print(
                f"Error processing notice: {e}"
            )

            continue


if __name__ == "__main__":
    crawl_admissions()