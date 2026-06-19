from apscheduler.schedulers.background import BackgroundScheduler
from app.crawler.crawler import crawl_admissions

scheduler = BackgroundScheduler()

def start_scheduler():

    print("INSIDE START_SCHEDULER")

    scheduler.add_job(
        crawl_admissions,
        "interval",
        minutes=1,
        id="college_crawler",
        replace_existing=True
    )

    print("JOB ADDED")

    scheduler.start()

    print("CRAWLER SCHEDULER STARTED")