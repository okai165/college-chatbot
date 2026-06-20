from sqlalchemy import text

with engine.connect() as conn:
    user = conn.execute(
        text("SELECT current_user")
    ).scalar()

    print("CURRENT USER =", user)