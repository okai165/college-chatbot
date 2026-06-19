import requests
from bs4 import BeautifulSoup

url = "https://www.gcwmaroad.edu.in/admissions.php"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

tables = soup.find_all("table")

print("TOTAL TABLES:", len(tables))

for i, table in enumerate(tables):

    print(f"\nTABLE {i+1}\n")

    print(
        table.get_text(
            separator="\n",
            strip=True
        )[:3000]
    )