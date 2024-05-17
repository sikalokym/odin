from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from pytz import utc
import logging
import os
import configparser
from src.ingest.cpam.services import get_supported_countries, ingest_all_cpam_data

def scheduled_task():
    try:
        # Call the function directly with the desired country parameter
        countries = get_supported_countries()
        for country in countries['CountryName']:
            ingest_all_cpam_data(country)
    except Exception as e:
        logging.error(f"Failed to complete scheduled task: {e}")

config = configparser.ConfigParser()
config.read('config/cpam.cfg')

env_var_name = config.get('REFRESH_DATE', 'ENV_VAR_NAME')
separator = config.get('REFRESH_DATE', 'ENV_VAR_NAME_SEPARATOR')
date = os.getenv('env_var_name', f'sun{separator}12')
day, hour = date.split(separator)
hour = int(hour)
cpam_scheduler = BackgroundScheduler(daemon=True, timezone=utc)
cpam_scheduler.add_job(scheduled_task, 'cron', day_of_week='sun', hour=12, minute=0)

# Shut down the scheduler when exiting the app
atexit.register(lambda: cpam_scheduler.shutdown())
