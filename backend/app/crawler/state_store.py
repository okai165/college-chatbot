import sqlite3
from threading import Lock

from app.crawler.url_normalizer import normalize_url


DB_PATH = "crawler_state.db"
_lock = Lock()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visited (
                url TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def is_visited(url: str) -> bool:
    url = normalize_url(url)

    with _lock:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                "SELECT 1 FROM visited WHERE url = ?",
                (url,)
            )
            return cur.fetchone() is not None


def mark_visited(url: str):
    url = normalize_url(url)

    with _lock:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO visited (url)
                VALUES (?)
                """,
                (url,)
            )
            conn.commit()


def clear_visited():
    with _lock:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM visited")
            conn.commit()