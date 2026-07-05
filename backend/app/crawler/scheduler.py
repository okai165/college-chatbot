from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from app.crawler.crawler import crawl_page, BASE_URL
from app.crawler.state_store import init_db, clear_visited   # ✅ use SQLite reset

scheduler = BackgroundScheduler()


def start_scheduler():
    print("INSIDE START_SCHEDULER")

    # ✅ Ensure DB and table exist before scheduling jobs
    init_db()

    START_PAGES = [
        BASE_URL,
        BASE_URL + "admissions.php",
        BASE_URL + "module.php?id=52",
        BASE_URL + "module.php?id=47",
        BASE_URL + "module.php?id=53",
        BASE_URL + "module.php?id=21",
        BASE_URL + "module.php?id=50",
        BASE_URL + "module.php?id=51",
        BASE_URL + "module.php?id=54",
        BASE_URL + "module.php?id=48",
        BASE_URL + "module.php?id=49",
        BASE_URL + "grievances.php",
        BASE_URL + "departments.php?id=40",
        BASE_URL + "Syllabus/Index/True?pp=UG",
        BASE_URL + "module.php?id=57",
        BASE_URL + "iqac.php",
        BASE_URL + "module.php?id=59",
    ]

    def run_unified_crawl():
        print("\n" + "=" * 60)
        print(f"STARTING UNIFIED CRAWL JOB at {datetime.now()}")
        print("=" * 60)

        # ✅ Reset persistent visited store
        clear_visited()

        # Crawl
        for page in START_PAGES:
            crawl_page(page)

        print("\n" + "=" * 60)
        print("UNIFIED CRAWL SUMMARY")
        print("=" * 60)
        print("Crawl completed successfully")
        print("=" * 60)

    scheduler.add_job(
        run_unified_crawl,
        trigger="interval",
        hours=3,
        next_run_time=datetime.now(),
        id="college_crawler",
        replace_existing=True,
    )

    print("JOB ADDED")
    scheduler.start()
    print("CRAWLER SCHEDULER STARTED")
