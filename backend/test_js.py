import requests

url = "https://www.gcwmaroad.edu.in/scripts/admissions.js"

response = requests.get(url)

print(response.text)