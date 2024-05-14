import logging
import time
import configparser

from src.database.db_operations import DBOperations
import src.ingest.cpam.api as cpam
from src.ingest.visa_files.services import assign_prices
from src.utils.ingest_utils import is_valid_car_type, is_valid_year

logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.read('config/cpam.cfg')

def ingest_all_cpam_data_from(year, country_code):
    """
    Ingests all CPAM data for a specific year and market.

    Args:
        year (int): The year for which the data needs to be ingested.
        country_code (str): The specific market for which the data needs to be ingested.

    Returns:
        tuple: A tuple containing two lists - `load_successfull` and `load_unsuccessfull`.
            `load_successfull` (list): A list of tuples representing the successfully loaded data.
                Each tuple contains the year and car type.
            `load_unsuccessfull` (list): A list of tuples representing the unsuccessfully loaded data.
                Each tuple contains the year and car type.
    """
    load_successfull = []
    load_unsuccessfull = []
    for car in cpam.get_car_types(year)['DataRows']:
        start_time_in = time.perf_counter()
        maf = config.get('SETTINGS', 'MARKET_AUTH_FLAG')
        sw = config.get('SETTINGS', 'START_WEEK')
        try:
            ingest_cpam_data(year, car['Type'], country_code, maf, sw)
            load_successfull.append((year, car['Type']))
        except Exception as e:
            logger.error(f'Error processing car type {car["Type"]}: {e}', extra={'country_code': country_code})
            load_unsuccessfull.append((year, car['Type']))
            continue
        end_time = time.perf_counter()
        duration = end_time - start_time_in
        logger.debug(f'Car {car["Type"]} execution time: {duration:.2f} seconds')
    return load_successfull, load_unsuccessfull

from multiprocessing import Process, Manager

def ingest_cpam_data_wrapper(year, car_type, country_code, maf, sw, load_successfull, load_unsuccessfull):
    try:
        ingest_cpam_data(year, car_type, country_code, maf, sw)
        load_successfull.append((year, car_type))
    except Exception as e:
        logger.error(f'Error processing car type {car_type}: {e}', extra={'country_code': country_code})
        load_unsuccessfull.append((year, car_type))

def ingest_all_cpam_data(country_code, year=None, start_model_year=''):
    with Manager() as manager:
        load_successfull = manager.list()
        load_unsuccessfull = manager.list()
        all_years = cpam.get_model_years(country_code, start_model_year=start_model_year)['Years'] if not year else [year]
        processes = []
        for year in all_years:
            for car in cpam.get_car_types(year, country_code)['DataRows']:
                maf = config.get('SETTINGS', 'MARKET_AUTH_FLAG')
                sw = config.get('SETTINGS', 'START_WEEK')
                p = Process(target=ingest_cpam_data_wrapper, args=(year, car['Type'], country_code, maf, sw, load_successfull, load_unsuccessfull))
                p.start()
                processes.append(p)
        for p in processes:
            p.join()
        logger.debug('CPAM data update completed', extra={'country_code': country_code})
        return list(load_successfull), list(load_unsuccessfull)
 
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
    logger.info(f'Processing car type: {car_type}', extra={'country_code': country_code})

    is_valid = is_valid_year(year, country_code)
    if isinstance(is_valid, str):
        raise ValueError(is_valid)
    elif not is_valid:
        raise ValueError('Invalid year')
    
    new_entities = DBOperations.instance.collect_entity(cpam.get_dictionary(year, car_type, country_code, maf, sw)['DataRows'], country_code)
    if not new_entities:
        return
    DBOperations.instance.collect_auth(cpam.get_authorization(year, car_type, country_code, maf, sw)['DataRows'], country_code)
    DBOperations.instance.collect_package(cpam.get_packages(year, car_type, country_code, maf, sw)['PackageDataRows'], country_code)
    DBOperations.instance.collect_dependency(cpam.get_dependency_rules(year, car_type, country_code, maf, sw)['DataRows'], country_code)
    DBOperations.instance.collect_feature(cpam.get_features(year, car_type, country_code, maf, sw)['DataRows'], country_code)
    
    logger.debug('Data insertion completed', extra={'country_code': country_code})

    assign_prices(country_code)

def get_supported_countries():
    """
    Gets the list of supported countries.

    Returns:
        list: A list of supported countries.
    """
    countries = DBOperations.instance.get_table_df(DBOperations.instance.config.get('SETTINGS', 'CountryCodes'), columns=['Code', 'CountryName'])
    return countries
