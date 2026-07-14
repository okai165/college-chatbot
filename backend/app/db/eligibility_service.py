from sqlalchemy import text
from app.db.database import engine



def save_eligibility(
    title,
    date,
    source_url,
    eligibility_list
):

    if not eligibility_list:
        return False


    with engine.begin() as conn:

        for item in eligibility_list:

            conn.execute(
                text("""
                    INSERT INTO eligibility
                    (
                        title,
                        eligibility,
                        source_url,
                        created_at
                    )
                    VALUES
                    (
                        :title,
                        :eligibility,
                        :source_url,
                        NOW()
                    )
                """),
                {
                    "title": title,
                    "eligibility": item,
                    "source_url": source_url
                }
            )

    return True