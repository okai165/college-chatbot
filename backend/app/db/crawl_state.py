from sqlalchemy import text


def get_page(db, url: str):
    result = db.execute(
        text("""
            SELECT id,
                   content_hash
            FROM crawled_pages
            WHERE url = :url
        """),
        {"url": url},
    )

    row = result.fetchone()

    if row:
        return {
            "id": row.id,
            "hash": row.content_hash,
        }

    return None


def insert_page(db, url, title, content_hash):
    db.execute(
        text("""
            INSERT INTO crawled_pages
            (
                url,
                title,
                content_hash,
                last_crawled
            )
            VALUES
            (
                :url,
                :title,
                :hash,
                NOW()
            )
        """),
        {
            "url": url,
            "title": title,
            "hash": content_hash,
        },
    )

    db.commit()


def update_page(db, url, title, content_hash):
    db.execute(
        text("""
            UPDATE crawled_pages
            SET
                title = :title,
                content_hash = :hash,
                last_crawled = NOW()
            WHERE url = :url
        """),
        {
            "url": url,
            "title": title,
            "hash": content_hash,
        },
    )

    db.commit()


def delete_chunks(db, url):
    db.execute(
        text("""
            DELETE
            FROM documents
            WHERE source_url = :url
        """),
        {"url": url},
    )

    db.commit()