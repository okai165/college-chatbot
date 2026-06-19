from bs4 import BeautifulSoup


def extract_updates(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    updates = []

    for tag in soup.find_all():

        text = tag.get_text(
            " ",
            strip=True
        )

        if "Admission Updates" in text:

            updates.append(text)

    return updates