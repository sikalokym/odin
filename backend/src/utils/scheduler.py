from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
import configparser
import datetime
import atexit
import os

from src.ingest.cpam.services import fetch_all_cpam_data, get_supported_countries, ingest_all_cpam_data, process_all_cpam_data
from src.database.db_connection import DatabaseConnection
from src.database.db_operations import DBOperations
from src.utils.sql_logging_handler import logger

# @author Hassan Wahba

def schedule_fetch_task():
    max_tries = 3
    for i in range(max_tries):
        try:
            DBOperations.create_instance(logger=logger)
            logger.info('Starting scheduled task to ingest CPAM data', extra={'country_code': 'All'})
            countries = get_supported_countries()
            for country in countries.Code.values:
                fetch_all_cpam_data(country)
            DatabaseConnection.close_connection()
            break
        except Exception as e:
            logger.error(f"Failed to complete scheduled task: {e}", extra={'country_code': 'All'})
            if i == max_tries - 1:
                break
    schedule_preprocess_task()

def schedule_preprocess_task():
    max_tries = 3
    for i in range(max_tries):
        try:
            DBOperations.create_instance(logger=logger)
            logger.info('Starting scheduled task to ingest CPAM data', extra={'country_code': 'All'})
            countries = get_supported_countries()
            current_year = datetime.datetime.now().year
            for country in countries.Code.values:
                process_all_cpam_data(country, current_year)
            DatabaseConnection.close_connection()
        except Exception as e:
            logger.error(f"Failed to complete scheduled task: {e}", extra={'country_code': 'All'})
            if i == max_tries - 1:
                break
    schedule_ingest_task()

def schedule_ingest_task():
    max_tries = 3
    for i in range(max_tries):
        try:
            DBOperations.create_instance(logger=logger)
            logger.info('Starting scheduled task to ingest CPAM data', extra={'country_code': 'All'})
            countries = get_supported_countries()
            current_year = datetime.datetime.now().year
            for country in countries.Code.values:
                ingest_all_cpam_data(country, start_model_year=current_year)
            DatabaseConnection.close_connection()
        except Exception as e:
            logger.error(f"Failed to complete scheduled task: {e}", extra={'country_code': 'All'})
            if i == max_tries - 1:
                break

config = configparser.ConfigParser()
config.read('config/cpam.cfg')

env_var_name = config.get('REFRESH_DATE', 'ENV_VAR_NAME')
separator = config.get('REFRESH_DATE', 'ENV_VAR_NAME_SEPARATOR')
date = os.getenv(env_var_name, f'mon{separator}4')

try:
    day, hour = date.split(separator)
    hour = int(hour)
except Exception as e:
    logger.error(f"Failed to parse the refresh date: {e}", extra={'country_code': 'All'})
    day, hour = 0, 4

cpam_scheduler = BackgroundScheduler(daemon=True, timezone=utc)
cpam_scheduler.add_job(schedule_fetch_task, 'cron', hour=hour, minute=3)
cpam_scheduler.add_job(schedule_fetch_task, 'cron', hour=hour+12, minute=30)

atexit.register(lambda: cpam_scheduler.shutdown())
