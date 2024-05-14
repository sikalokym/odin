from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from pytz import utc
import logging

from src.ingest.cpam.services import get_supported_countries, ingest_all_cpam_data

def scheduled_task():
    try:
        # Call the function directly with the desired country parameter
        countries = get_supported_countries()
        for country in countries['CountryName']:
            ingest_all_cpam_data(country)
    except Exception as e:
        logging.error(f"Failed to complete scheduled task: {e}")

cpam_scheduler = BackgroundScheduler(daemon=True, timezone=utc)
cpam_scheduler.add_job(scheduled_task, 'cron', day_of_week='sun', hour=12, minute=0)

# Shut down the scheduler when exiting the app
atexit.register(lambda: cpam_scheduler.shutdown())
