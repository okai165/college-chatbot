from scrapers.admission_updates import get_admission_updates

updates = get_admission_updates()

print(f"\nFound {len(updates)} admission notices\n")

for item in updates:
    print("=" * 60)
    print("Title :", item["title"])
    print("Date  :", item["date"])
    print("File  :", item["file_url"])