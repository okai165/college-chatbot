from .base_scraper import get_soup

def get_fee_structure():

    soup = get_soup()

    link = soup.find(
        "a",
        string=lambda x:
        x and
        "Fee Structure"
        in x
    )

    if not link:
        return None

    return {
        "title":
        link.get_text(
            strip=True
        ),
        "pdf":
        link.get("href")
    }