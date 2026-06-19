import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_admission_committee():

    url = "https://www.gcwmaroad.edu.in/admissions.php"

    response = requests.get(url)

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    tables = pd.read_html(str(soup))

    committee = tables[0]

    return committee.to_dict(
        orient="records"
    )