from .base_scraper import get_soup

def get_document_checklist():

    soup = get_soup()

    text = soup.find(
        string=lambda x:
        x and
        "Document Uploading"
        in x
    )

    if not text:
        return []

    ul = text.parent.find_next("ul")

    if not ul:
        return []

    documents = []

    for li in ul.find_all(
        "li",
        recursive=False
    ):
        documents.append(
            li.get_text(
                strip=True
            )
        )

    return documents