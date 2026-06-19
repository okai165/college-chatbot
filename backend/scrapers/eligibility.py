from .base_scraper import get_soup

def get_eligibility():

    soup = get_soup()

    heading = soup.find(
        "h5",
        string=lambda x:
        x and "Eligibility" in x
    )

    if not heading:
        return []

    ol = heading.find_next("ol")

    if not ol:
        return []

    return [

        li.get_text(
            strip=True
        )

        for li in ol.find_all("li")
    ]