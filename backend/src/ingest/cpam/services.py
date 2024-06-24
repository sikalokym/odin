from cachetools import cached, TTLCache
import pandas as pd
import configparser
import time

from src.database.db_operations import DBOperations
from src.ingest.visa_files.services import ingest_visa_data
from src.utils.sql_logging_handler import logger
import src.ingest.cpam.api as cpam

config = configparser.ConfigParser()
config.read('config/cpam.cfg')

def ingest_all_cpam_data_from(year, country_code):
    """
    Ingests all CPAM data for a specific year and market.

    Args:
        year (int): The year for which the data needs to be ingested.
        country_code (str): The specific market for which the data needs to be ingested.

    Returns:
        tuple: A tuple containing two lists - `load_successful` and `load_unsuccessful`.
            `load_successful` (list): A list of tuples representing the successfully loaded data.
                Each tuple contains the year and car type.
            `load_unsuccessful` (list): A list of tuples representing the unsuccessfully loaded data.
                Each tuple contains the year and car type.
    """
    load_successful = []
    load_unsuccessful = []
    for car in cpam.get_car_types(year)['DataRows']:
        start_time_in = time.perf_counter()
        maf = config.get('SETTINGS', 'MARKET_AUTH_FLAG')
        sw = config.get('SETTINGS', 'START_WEEK')
        try:
            ingest_cpam_data(year, car['Type'], country_code, maf, sw)
            load_successful.append((year, car['Type']))
        except Exception as e:
            logger.error(f'Error processing car type {car["Type"]}: {e}', extra={'country_code': country_code})
            load_unsuccessful.append((year, car['Type']))
        end_time = time.perf_counter()
        duration = end_time - start_time_in
        logger.debug(f'Car {car["Type"]} execution time: {duration:.2f} seconds')
    return load_successful, load_unsuccessful

def ingest_all_cpam_data(country_code, year=None, start_model_year=''):
    load_successful = []
    load_unsuccessful = []
    if year:
        all_years = [year]
    else:
        all_years = cpam.get_model_years(country_code, start_model_year=start_model_year)
        if not all_years or all_years == []:
            logger.error('No model years found', extra={'country_code': country_code})
            return load_successful, load_unsuccessful
    maf = config.get('SETTINGS', 'MARKET_AUTH_FLAG')
    sw = config.get('SETTINGS', 'START_WEEK')
    for year in all_years:
        for car in cpam.get_car_types(year, country_code)['DataRows']:
            if car['Type'] != '246':
                continue
            try:
                ingest_cpam_data(year, car['Type'], country_code, maf, sw)
                load_successful.append((year, car['Type']))
            except Exception as e:
                logger.error(f'Error processing car type {car["Type"]}: {e}', extra={'country_code': country_code})
                load_unsuccessful.append((year, car['Type']))
    logger.debug('CPAM data update completed', extra={'country_code': country_code})
    return load_successful, load_unsuccessful

def ingest_cpam_data(year, car_type, country_code, maf, sw):
    """
    Ingests CPAM data for a specific year, car type, spec market, MAF, and SW.

    Args:
        year (int): The year of the data.
        car_type (str): The type of car.
        country_code (str): The specific market.
        maf (str): The MAF value.
        sw (str): The SW value.

    Raises:
        ValueError: If the year or car type is invalid.
    """
    logger.info(f'Processing car type: {car_type}')

    new_entities = DBOperations.instance.collect_entity(cpam.get_dictionary(year, car_type, country_code, maf, sw).get('DataRows', None), country_code)
    if not new_entities:
        return
    DBOperations.instance.collect_auth(cpam.get_authorization(year, car_type, country_code, maf, sw).get('DataRows', None), country_code)
    DBOperations.instance.collect_package(cpam.get_packages(year, car_type, country_code, maf, sw).get('PackageDataRows', None), country_code)
    DBOperations.instance.collect_dependency(cpam.get_dependency_rules(year, car_type, country_code, maf, sw).get('DataRows', None), country_code)
    DBOperations.instance.collect_feature(cpam.get_features(year, car_type, country_code, maf, sw).get('DataRows', None), country_code)
    DBOperations.instance.consolidate_translations(country_code)
    
    logger.debug('Data insertion completed', extra={'country_code': country_code})

    ingest_visa_data(country_code)

cache = TTLCache(maxsize=100, ttl=60)

@cached(cache)
def get_supported_countries(country_code=None):
    """
    Gets the list of supported countries.

    Returns:
        list: A list of supported countries.
    """
    try:
        conditions = ['1=1'] if not country_code else [f"Code = '{country_code}'"]
        
        countries = DBOperations.instance.get_table_df(DBOperations.instance.config.get('SETTINGS', 'CountryCodes'), columns=['Code', 'CountryName'], conditions=conditions)
        return countries
    except Exception as e:
        logger.error(f'Failed to get supported countries: {e}', extra={'country_code': 'All'})
        return pd.DataFrame()
