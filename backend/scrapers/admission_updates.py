import requests

API_URL = "https://gcwmaroad.edu.in/src/fetchnotices.php"


def get_admission_updates():
    try:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()

        data = response.json()
        notices = data.get("noticeData", [])

        admission_notices = []

        for notice in notices:

            # notice_type = 1 => Admissions
            if int(notice.get("notice_type", 0)) == 1:

                admission_notices.append({
                    "id": notice.get("id"),
                    "title": notice.get("title"),
                    "date": notice.get("published_at"),
                    "file_url": (
                        f"https://gcwmaroad.edu.in/docs/{notice.get('docurl')}"
                        if notice.get("docurl")
                        else None
                    )
                })

        return admission_notices

    except Exception as e:
        print("Admission scraper error:", e)
        return []