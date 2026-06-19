import requests

url = "https://gcwmaroad.edu.in/src/fetchnotices.php"

response = requests.get(url)

print("Status:", response.status_code)
print(response.text[:1000])