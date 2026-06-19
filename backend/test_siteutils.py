import requests

url = "https://www.gcwmaroad.edu.in/scripts/siteUtils.js"

response = requests.get(url)

with open("siteUtils.js", "w", encoding="utf-8") as f:
    f.write(response.text)

print("saved")