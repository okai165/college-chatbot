import requests

API_URL = "https://gcwmaroad.edu.in/src/fetchnotices.php"


def get_admission_updates():

    response = requests.get(
        API_URL,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    notices = data.get(
        "noticeData",
        []
    )

    results = []

    for notice in notices:

        if int(
            notice.get(
                "notice_type",
                0
            )
        ) == 1:

            results.append(
                {
                    "title": notice.get(
                        "title"
                    ),
                    "date": notice.get(
                        "published_at"
                    ),
                    "pdf_url": (
                        f"https://gcwmaroad.edu.in/docs/{notice.get('docurl')}"
                        if notice.get("docurl")
                        else None
                    )
                }
            )

    return results