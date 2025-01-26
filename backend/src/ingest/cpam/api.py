import configparser
import requests
import logging
import os

from src.utils.xml_templates import model_year_resp_template, car_types_resp_template, dictionary_resp_template, authorization_resp_template, packages_resp_template, dependency_rules_resp_template, features_resp_template
from src.utils.xml_templates import model_year_req_xml, car_types_req_xml, dictionary_req_xml, authorization_req_xml, packages_req_xml, dependency_rules_req_xml, features_req_xml
from src.utils.parse_xml import parse_xml

# @author Hassan Wahba

# logger = logging.getLogger(__name__)
from src.utils.sql_logging_handler import (
    logger,
    cpam_processing_logger,
    cpam_processing_cartype_logger
)

config = configparser.ConfigParser()
config.read('config/cpam.cfg')

# Connection
API_URL = os.environ.get('CPAM_API_URL')
HEADERS = {'user-key': os.environ.get('CPAM_USER_KEY')}

# Settings
CONSUMER = config.get('SETTINGS', 'CONSUMER')

# Requests Data types
MODEL_YEAR = config.get('REQ_DATA_TYPES', 'MODEL_YEAR')
CAR_TYPES = config.get('REQ_DATA_TYPES', 'CAR_TYPES')
DICTIONARY = config.get('REQ_DATA_TYPES', 'DICTIONARY')
AUTHORIZATION = config.get('REQ_DATA_TYPES', 'AUTHORIZATION')
PACKAGE = config.get('REQ_DATA_TYPES', 'PACKAGE')
DEPENDENCY_RULES = config.get('REQ_DATA_TYPES', 'DEPENDENCY_RULES')
FEATURES = config.get('REQ_DATA_TYPES', 'FEATURES')

# Response PNO Data types
PNO_CAR_TYPE= config.get('RESP_PNO_DATA_TYPES', 'CAR_TYPE')
PNO_ENGINE= config.get('RESP_PNO_DATA_TYPES', 'ENGINE')
PNO_SALES_VERSION= config.get('RESP_PNO_DATA_TYPES', 'SALES_VERSION')
PNO_BODY= config.get('RESP_PNO_DATA_TYPES', 'BODY')
PNO_GEARBOX= config.get('RESP_PNO_DATA_TYPES', 'GEARBOX')
PNO_STEERING= config.get('RESP_PNO_DATA_TYPES', 'STEERING')
PNO_MARKETING_CODE= config.get('RESP_PNO_DATA_TYPES', 'MARKETING_CODE')


def get_model_years(spec_market, start_model_year=''):
    """ Fetch available model years from CPAM.
    
    Args:
        start_model_year (str): Start model year. Empty will give data from current model year and onwards
    
    Returns:
        str: XML response from CPAM
    """
    logger.info('Fetching model years from CPAM')
    req = model_year_req_xml.format(CONSUMER, MODEL_YEAR, spec_market, start_model_year)
    # logger.debug(req)
    try:
        response = requests.post(API_URL, headers=HEADERS, data=req)
    except requests.exceptions.RequestException as e:
        logger.error(f'Error fetching model years from CPAM: {e}')
        return []

    if response.status_code > 500:
        logger.error('Error fetching model years from CPAM')
        return []
    
    logger.info('Model years fetched from CPAM')
    return parse_xml(response.text, model_year_resp_template)

def get_car_types(model_year, spec_market):
    """ Fetch available car types from CPAM.

    Args:
        model_year (str): Model year

    Returns:
        str: XML response from CPAM
    """
    cpam_processing_logger.info('Fetching car types from CPAM', extra={'country': spec_market, 'year': model_year})
    req = car_types_req_xml.format(CONSUMER, CAR_TYPES, spec_market, model_year)
    logger.debug(req)

    response = requests.post(API_URL, headers=HEADERS, data=req)

    if response.status_code > 500:
        cpam_processing_logger.error('Error fetching car types from CPAM', extra={'country': spec_market, 'year': model_year})
        return []
    
    cpam_processing_logger.info('Car types fetched from CPAM', extra={'country': spec_market, 'year': model_year})
    return parse_xml(response.text, car_types_resp_template)

def get_dictionary(model_year, car_type, spec_market, market_auth_flag='', start_week=''):
    """ Fetch dictionary from CPAM.
    
    Args:
        car_type (str): Car type
        model_year (str): Model year
        market_auth_flag (str): Market auth flag M to get only Market authorized products (NSC offer). Empty to get full Business authorization for the market (central offer)
        start_week (str): Start week. CURR will give data from current structure week and onwards, not any historical weeks. Empty will give data for the full mode year

    Returns:
        str: XML response from CPAM
    """
    cpam_processing_cartype_logger.info('Fetching dictionary from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    req = dictionary_req_xml.format(CONSUMER, DICTIONARY, spec_market, car_type, model_year, market_auth_flag, start_week)
    # logger.debug(req)

    response = requests.post(API_URL, headers=HEADERS, data=req)
    
    if response.status_code > 500:
        cpam_processing_cartype_logger.error('Error fetching dictionary from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
        return dict()
    
    cpam_processing_cartype_logger.info('Dictionary fetched from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    return parse_xml(response.text, dictionary_resp_template)

def get_authorization(model_year, car_type, spec_market, market_auth_flag='', start_week=''):
    """ Fetch authorization from CPAM.
    
    Args:
        car_type (str): Car type
        model_year (str): Model year
        market_auth_flag (str): Market auth flag M to get only Market authorized products (NSC offer). Empty to get full Business authorization for the market (central offer)
        start_week (str): Start week. CURR will give data from current structure week and onwards, not any historical weeks. Empty will give data for the full mode year

    Returns:
        str: XML response from CPAM
    """
    cpam_processing_cartype_logger.info('Fetching authorization from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    req = authorization_req_xml.format(CONSUMER, AUTHORIZATION, spec_market, car_type, model_year, market_auth_flag, start_week)
    # logger.debug(req)

    response = requests.post(API_URL, headers=HEADERS, data=req)
    
    if response.status_code > 500:
        cpam_processing_cartype_logger.error('Error fetching authorization from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
        return dict()
    
    cpam_processing_cartype_logger.info('Authorization fetched from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    return parse_xml(response.text, authorization_resp_template)

def get_packages(model_year, car_type, spec_market, market_auth_flag='m', start_week=''):
    """ Fetch packages from CPAM.
    
    Args:
        car_type (str): Car type
        model_year (str): Model year
        market_auth_flag (str): Market auth flag M to get only Market authorized products (NSC offer). Empty to get full Business authorization for the market (central offer)
        start_week (str): Start week. CURR will give data from current structure week and onwards, not any historical weeks. Empty will give data for the full mode year

    Returns:
        str: XML response from CPAM
    """
    cpam_processing_cartype_logger.info('Fetching packages from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    req = packages_req_xml.format(CONSUMER, PACKAGE, spec_market, car_type, model_year, market_auth_flag, start_week)
    # logger.debug(req)

    response = requests.post(API_URL, headers=HEADERS, data=req)
    
    if response.status_code > 500:
        cpam_processing_cartype_logger.error('Error fetching packages from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
        return dict()
    
    cpam_processing_cartype_logger.info('Packages fetched from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    return parse_xml(response.text, packages_resp_template)

def get_dependency_rules(model_year, car_type, spec_market, market_auth_flag='', start_week=''):
    """ Fetch dependency rules from CPAM.
    
    Args:
        car_type (str): Car type
        model_year (str): Model year
        market_auth_flag (str): Market auth flag M to get only Market authorized products (NSC offer). Empty to get full Business authorization for the market (central offer)
        start_week (str): Start week. CURR will give data from current structure week and onwards, not any historical weeks. Empty will give data for the full mode year

    Returns:
        str: XML response from CPAM
    """
    cpam_processing_cartype_logger.info('Fetching dependency rules from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    req = dependency_rules_req_xml.format(CONSUMER, DEPENDENCY_RULES, spec_market, car_type, model_year, market_auth_flag, start_week)
    # logger.debug(req)

    response = requests.post(API_URL, headers=HEADERS, data=req)
    
    if response.status_code > 500:
        cpam_processing_cartype_logger.error('Error fetching dependency rules from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
        return dict()
    
    cpam_processing_cartype_logger.info('Dependency rules fetched from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    return parse_xml(response.text, dependency_rules_resp_template)

def get_features(model_year, car_type, spec_market, market_auth_flag='', start_week=''):
    """ Fetch features from CPAM.
    
    Args:
        car_type (str): Car type
        model_year (str): Model year
        market_auth_flag (str): Market auth flag M to get only Market authorized products (NSC offer). Empty to get full Business authorization for the market (central offer)
        start_week (str): Start week. CURR will give data from current structure week and onwards, not any historical weeks. Empty will give data for the full mode year

    Returns:
        str: XML response from CPAM
    """
    cpam_processing_cartype_logger.info('Fetching features from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    req = features_req_xml.format(CONSUMER, FEATURES, spec_market, car_type, model_year, market_auth_flag, start_week)
    # logger.debug(req)

    response = requests.post(API_URL, headers=HEADERS, data=req)
    
    if response.status_code > 500:
        cpam_processing_cartype_logger.error('Error fetching features from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
        return dict()
    
    cpam_processing_cartype_logger.info('Features fetched from CPAM', extra={'country': spec_market, 'year': model_year, 'cartype': car_type})
    return parse_xml(response.text, features_resp_template)
