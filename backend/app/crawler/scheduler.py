from apscheduler.schedulers.background import BackgroundScheduler
from app.crawler.crawler import crawl_page, write_summary, BASE_URL
from datetime import datetime

scheduler = BackgroundScheduler()

def start_scheduler():
    print("INSIDE START_SCHEDULER")

    START_PAGES = [
        BASE_URL,
        BASE_URL + "admissions.php",
        BASE_URL + "aboutus.php",
        BASE_URL + "public_disclosure.php",
        BASE_URL + "academics.php",
        BASE_URL + "research.php",
        BASE_URL + "entrepreneurship.php",
        BASE_URL + "student_corner.php",
        BASE_URL + "iqac.php",
        BASE_URL + "nirf.php",
        BASE_URL + "login.php"
    ]

    def run_unified_crawl():
        from app.crawler import crawler
        # Reset counters and state at the start of each run
        crawler.saved = 0
        crawler.skipped = 0
        crawler.failed = 0
        crawler.downloaded_files.clear()
        crawler.visited.clear()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("\n" + "="*60)
        print(f"STARTING UNIFIED CRAWL JOB at {timestamp}")
        print("="*60)

        for page in START_PAGES:
            crawl_page(page)

        write_summary()

    # Schedule the unified crawler every 3 hours
    scheduler.add_job(
        run_unified_crawl,
        "interval",
        hours=3,
        next_run_time=datetime.now(),
        id="college_crawler",
        replace_existing=True
    )

    print("JOB ADDED")
    scheduler.start()
    print("CRAWLER SCHEDULER STARTED")
