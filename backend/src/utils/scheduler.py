from src.database.db_connection import DatabaseConnection
from src.database.db_operations import DBOperations
from src.ingest.cpam.services import get_supported_countries, ingest_all_cpam_data
from src.utils.sql_logging_handler import logger
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
import configparser
import atexit
import os


def scheduled_task():
    try:
        DBOperations.create_instance(logger=logger)
        countries = get_supported_countries()
        for country in countries:
            ingest_all_cpam_data(country)
        DatabaseConnection.close_connection()
    except Exception as e:
        logger.error(f"Failed to complete scheduled task: {e}", extra={'country_code': country})

config = configparser.ConfigParser()
config.read('config/cpam.cfg')

env_var_name = config.get('REFRESH_DATE', 'ENV_VAR_NAME')
separator = config.get('REFRESH_DATE', 'ENV_VAR_NAME_SEPARATOR')
date = os.getenv('env_var_name', f'mon{separator}9')

try:
    day, hour = date.split(separator)
    hour = int(hour)
except Exception as e:
    logger.error(f"Failed to parse the refresh date: {e}", extra={'country_code': 'All'})
    day, hour = 'mon', 9

cpam_scheduler = BackgroundScheduler(daemon=True, timezone=utc)

cpam_scheduler.add_job(scheduled_task, 'cron', day_of_week=day, hour=hour, minute=3)

# Shut down the scheduler when exiting the app
atexit.register(lambda: cpam_scheduler.shutdown())
