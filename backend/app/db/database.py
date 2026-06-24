import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

env_path = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(dotenv_path=env_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL =", DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# TEMPORARY DEBUG
with engine.connect() as conn:
    user = conn.execute(
        text("SELECT current_user")
    ).scalar()

    print("CURRENT USER =", user)