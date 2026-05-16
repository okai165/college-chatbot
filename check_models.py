from dotenv import load_dotenv
load_dotenv()

import os
from google import genai

print("KEY:", os.getenv("GOOGLE_API_KEY"))

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

models = client.models.list()

for m in models:
    print(m.name)