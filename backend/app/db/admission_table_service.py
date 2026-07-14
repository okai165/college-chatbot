from sqlalchemy import text
from app.db.database import engine
import json


def save_admission_table(title, table_data):
    try:
        print("\n========== SAVE ADMISSION TABLE ==========")
        print("TITLE:", title)

        with engine.begin() as conn:

            # Remove old admission data with same title
            conn.execute(
                text("""
                    DELETE FROM admission_tables
                    WHERE title = :title
                """),
                {
                    "title": title
                }
            )

            # Insert fresh data
            conn.execute(
                text("""
                    INSERT INTO admission_tables
                    (
                        title,
                        table_data
                    )
                    VALUES
                    (
                        :title,
                        CAST(:table_data AS jsonb)
                    )
                """),
                {
                    "title": title,
                    "table_data": json.dumps(table_data)
                }
            )

        print("Admission table saved successfully")

    except Exception as e:
        print("ADMISSION TABLE SAVE ERROR:", e)



def get_admission_table():

    try:
        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT
                        id,
                        title,
                        table_data,
                        created_at
                    FROM admission_tables
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
            )

            row = result.fetchone()

            if not row:
                return None

            return dict(row._mapping)

    except Exception as e:
        print("ADMISSION TABLE FETCH ERROR:", e)
        return None