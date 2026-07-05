import sqlite3
from threading import Lock

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
    with _lock:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute("SELECT 1 FROM visited WHERE url = ?", (url,))
            return cur.fetchone() is not None


def mark_visited(url: str):
    with _lock:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO visited (url) VALUES (?)",
                (url,)
            )
            conn.commit()


def clear_visited():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM visited")
        conn.commit()