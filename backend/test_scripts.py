from scrapers.base_scraper import get_soup

soup = get_soup()

for script in soup.find_all("script"):
    if script.get("src"):
        print(script["src"])