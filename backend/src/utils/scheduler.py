from src.ingest.cpam.services import get_supported_countries, ingest_all_cpam_data
from src.utils.sql_logging_handler import logger
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
import configparser
import atexit
import os


def scheduled_task(country):
    try:
        ingest_all_cpam_data(country)
    except Exception as e:
        logger.error(f"Failed to complete scheduled task: {e}", extra={'country_code': country})

config = configparser.ConfigParser()
config.read('config/cpam.cfg')

env_var_name = config.get('REFRESH_DATE', 'ENV_VAR_NAME')
separator = config.get('REFRESH_DATE', 'ENV_VAR_NAME_SEPARATOR')
date = os.getenv('env_var_name', f'mon{separator}9')
minute = 1
job_duration = 20

try:
    day, hour = date.split(separator)
    hour = int(hour)
except Exception as e:
    logger.error(f"Failed to parse the refresh date: {e}", extra={'country_code': 231})
    day, hour = 'mon', 9

cpam_scheduler = BackgroundScheduler(daemon=True, timezone=utc)

countries = get_supported_countries()
for country in countries:
    cpam_scheduler.add_job(scheduled_task, 'cron', day_of_week=day, hour=hour, minute=minute, args=[country], id=f'cpam_{country}', replace_existing=True)
    minute += job_duration

# Shut down the scheduler when exiting the app
atexit.register(lambda: cpam_scheduler.shutdown())
