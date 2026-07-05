from bs4 import BeautifulSoup

def extract_content(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts, styles, noscript
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Get all text in one go
    text = soup.get_text(separator="\n", strip=True)

    # Filter out junk lines
    data = [line for line in text.splitlines() if len(line.strip()) > 3]

    return data
