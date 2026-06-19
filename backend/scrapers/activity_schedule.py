from .base_scraper import get_soup

def get_activity_schedule():

    soup = get_soup()

    table = soup.find(
        id="admTl"
    )

    if not table:
        return []

    rows = []

    for tr in table.find_all("tr"):

        cols = [
            td.get_text(
                strip=True
            )
            for td in tr.find_all(
                ["td", "th"]
            )
        ]

        if cols:
            rows.append(cols)

    return rows