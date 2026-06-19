import requests
from bs4 import BeautifulSoup

URL = "https://www.gcwmaroad.edu.in/admissions.php"

def get_soup():
    response = requests.get(URL, timeout=20)

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser"
    )