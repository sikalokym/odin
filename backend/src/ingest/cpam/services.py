from cachetools import cached, TTLCache
import pandas as pd
import configparser
import time

from src.database.db_operations import DBOperations
from src.ingest.visa_files.services import ingest_visa_data
from src.utils.ingest_utils import get_authorization_status
from src.utils.sql_logging_handler import logger
from src.ingest.visa_files import preprocess
import src.ingest.cpam.api as cpam
import src.utils.db_utils as utils

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
        logger.info(f'Car {car["Type"]} execution time: {duration:.2f} seconds')
    return load_successful, load_unsuccessful

def ingest_all_cpam_data(country_code, year=None, start_model_year=''):
    load_successful = []
    load_unsuccessful = []
    logger.info('Starting CPAM data update', extra={'country_code': country_code})
    if year:
        all_years = [year]
    else:
        all_years = cpam.get_model_years(country_code, start_model_year=start_model_year)
        if not all_years or all_years == []:
            logger.error('No model years found', extra={'country_code': country_code})
            return load_successful, load_unsuccessful
        else:
            all_years = all_years['Years']
    maf = config.get('SETTINGS', 'MARKET_AUTH_FLAG')
    sw = config.get('SETTINGS', 'START_WEEK')
    for year in all_years:
        for car in cpam.get_car_types(year, country_code)['DataRows']:
            print(f'Processing car type: {car["Type"]}')
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

    # global_dict_auth = utils.df_from_datarows(cpam.get_dictionary(year, car_type, country_code, '', sw).get('DataRows', None))
    # market_dict_auth = utils.df_from_datarows(cpam.get_dictionary(year, car_type, country_code, 'm', sw).get('DataRows', None))
    
    # if market_dict_auth.empty:
    #     logger.error('No data found for the market', extra={'country_code': country_code})
    #     return
    
    global_authorization_auth = utils.df_from_datarows(cpam.get_authorization(year, car_type, country_code, '', sw).get('DataRows', None), ['Code', 'DataType'])
    market_authorization_auth = utils.df_from_datarows(cpam.get_authorization(year, car_type, country_code, 'm', sw).get('DataRows', None), ['Code', 'DataType'])
    
    authorized_packages = utils.df_from_package_datarows(cpam.get_packages(year, car_type, country_code, 'm', sw).get('PackageDataRows', None))
    
    global_dependency_auth = utils.df_from_datarows(cpam.get_dependency_rules(year, car_type, country_code, '', sw).get('DataRows', None), ['RuleCode', 'ItemCode', 'FeatureCode']).explode('FeatureCode')
    market_dependency_auth = utils.df_from_datarows(cpam.get_dependency_rules(year, car_type, country_code, 'm', sw).get('DataRows', None), ['RuleCode', 'ItemCode', 'FeatureCode']).explode('FeatureCode')
    
    global_feat_auth = utils.df_from_datarows(cpam.get_features(year, car_type, country_code, '', sw).get('DataRows', None), ['Code', 'Special', 'Reference'])
    market_feat_auth = utils.df_from_datarows(cpam.get_features(year, car_type, country_code, 'm', sw).get('DataRows', None), ['Code', 'Special', 'Reference'])
    
    # authorized_dictionaries, unauthorized_dictionaries = get_authorization_status(global_dict_auth, market_dict_auth)
    authorized_authorizations, unauthorized_authorizations = get_authorization_status(global_authorization_auth, market_authorization_auth)
    authorized_dependencies, unauthorized_dependencies = get_authorization_status(global_dependency_auth, market_dependency_auth)
    authorized_features, unauthorized_features = get_authorization_status(global_feat_auth, market_feat_auth)
    
    # DBOperations.instance.collect_entity(authorized_dictionaries, country_code)
    # DBOperations.instance.collect_auth(authorized_authorizations, country_code)
    DBOperations.instance.collect_package(authorized_packages, country_code)
    DBOperations.instance.collect_dependency(authorized_dependencies, country_code)
    DBOperations.instance.collect_feature(authorized_features, country_code)
    
    DBOperations.instance.drop_feature(unauthorized_features, country_code)
    DBOperations.instance.drop_dependency(unauthorized_dependencies, country_code)
    DBOperations.instance.drop_auth(unauthorized_authorizations, country_code)
    ### Don't drop entities because you might drop something used in a previous processed car type
    # DBOperations.instance.drop_entity(unauthorized_dictionaries, country_code)
    
    DBOperations.instance.consolidate_translations(country_code)
    
    logger.info('Data insertion completed', extra={'country_code': country_code})

    conditions = [f"CountryCode = '{country_code}'", f"ModelYear = '{year}'", f"CarType = '{car_type}'"]
    df_raw = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), conditions=conditions)
    df_processed = preprocess.process_visa_df(df_raw)
    df_processed.insert(7, 'CountryCode', country_code)
    ingest_visa_data(country_code, df_processed)

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
