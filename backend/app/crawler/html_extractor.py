from bs4 import BeautifulSoup


def extract_headings(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    data = []

    for heading in soup.find_all(
        ["h1", "h2", "h3", "h4"]
    ):

        text = heading.get_text(
            strip=True
        )

        if len(text) > 3:

            data.append(text)

    return data