import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

# database.py is in: backend/app/db/database.py
# parents[3] = Project folder (where your .env currently is)
env_path = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(dotenv_path=env_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)