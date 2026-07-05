import requests

headers = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_html(url: str):
    try:
        res = requests.get(url, headers=headers, timeout=20)

        if res.status_code != 200:
            return ""

        return res.text

    except Exception:
        return ""