from app.crawler.dynamic_module_crawler import fetch_department_profile

data = fetch_department_profile(48)

print(data["title"])
print("=" * 80)
print(data["content"])