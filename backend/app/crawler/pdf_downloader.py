import os
import requests

DOWNLOAD_DIR = "app/crawler/downloads"

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)

def download_pdf(url):

    filename = url.split("/")[-1]

    save_path = os.path.join(
        DOWNLOAD_DIR,
        filename
    )

    response = requests.get(
        url,
        timeout=60
    )

    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path