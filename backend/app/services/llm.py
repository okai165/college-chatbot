import os
from google import genai

# IMPORTANT: set GOOGLE_API_KEY in environment
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))