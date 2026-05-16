import sys
from sqlalchemy import text
from app.db.database import engine
from app.core.security import hash_password

if len(sys.argv) < 3:
    print("Usage: python create_admin.py <username> <password>")
    raise SystemExit(1)

username = sys.argv[1]
password = sys.argv[2]

pw_hash = hash_password(password)

with engine.begin() as conn:
    conn.execute(
        text("""
            INSERT INTO admin_users (username, password_hash)
            VALUES (:u, :p)
            ON CONFLICT (username) DO UPDATE SET password_hash=:p
        """),
        {"u": username, "p": pw_hash},
    )

print("Admin user created/updated:", username)