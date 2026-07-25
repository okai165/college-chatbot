import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path("C:/Users/Elite Fusion Tech/OneDrive/Desktop/Project/.env")

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    print(f"✅ Loaded .env from: {ENV_PATH}")
else:
    raise FileNotFoundError(f".env file not found at {ENV_PATH}")

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")

print("DEBUG: Raw LLM_API_KEY =", repr(LLM_API_KEY))
print("DEBUG: Raw LLM_BASE_URL =", repr(LLM_BASE_URL))

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-now")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

missing = []
if not LLM_API_KEY:
    missing.append("LLM_API_KEY")
if not LLM_BASE_URL:
    missing.append("LLM_BASE_URL")

if missing:
    raise ValueError(f"❌ Missing environment variables: {missing}\nChecked .env at: {ENV_PATH}")

print("✅ ENV LOADED SUCCESSFULLY")