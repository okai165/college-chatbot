from app.db.database import get_connection

def save_notification(data):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO notifications(
            title,
            category,
            summary,
            start_date,
            last_date,
            eligibility,
            required_documents,
            source_url
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)

        ON CONFLICT(source_url)
        DO NOTHING
        """,
        (
            data["title"],
            data["category"],
            data["summary"],
            data["start_date"],
            data["last_date"],
            data["eligibility"],
            data["required_documents"],
            data["source_url"]
        )
    )

    conn.commit()

    cur.close()

    conn.close()