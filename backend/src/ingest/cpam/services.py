from cachetools import cached, TTLCache
import pandas as pd
import configparser
import os

from src.ingest.visa_files.preprocess import process_visa_df
from src.ingest.visa_files.services import ingest_visa_data
from src.utils.ingest_utils import get_authorization_status
from src.database.db_operations import DBOperations
from src.utils.sql_logging_handler import logger
import src.ingest.cpam.api as cpam
import src.utils.db_utils as utils


config = configparser.ConfigParser()
config.read('config/cpam.cfg')

def fetch_all_cpam_data(country_code, year=None, start_model_year=''):
    logger.info('Starting CPAM data fetching', extra={'country_code': country_code})
    
    if year:
        all_years = [year]
    else:
        all_years = cpam.get_model_years(country_code, start_model_year=start_model_year)
        if not all_years or all_years == []:
            logger.error('No model years found', extra={'country_code': country_code})
            return
        else:
            all_years = all_years['Years']
    sw = config.get('SETTINGS', 'START_WEEK')
    for year in all_years:
        for car in cpam.get_car_types(year, country_code)['DataRows']:
            print(f'Fetching car type: {car["Type"]}')
            try:
                fetch_cpam_data(year, car['Type'], country_code, sw)
            except Exception as e:
                logger.error(f'Error fetching car type {car["Type"]}: {e}', extra={'country_code': country_code})
    
    logger.debug('CPAM data fetching completed', extra={'country_code': country_code})

def process_all_cpam_data(country_code, start_model_year=0):
    logger.info('Starting CPAM data preprocessing', extra={'country_code': country_code})
    folder = f"{os.getcwd()}/dist/cpam_data/{country_code}/"
    for sub_folder in os.listdir(folder):
        new_folder = folder + sub_folder + '/'
        if not os.path.isdir(new_folder) or int(sub_folder) < start_model_year:
            continue
        print(f'Processing Year: {sub_folder}')
        for subsub_folder in os.listdir(new_folder):
            if not os.path.isdir(new_folder + subsub_folder):
                continue
            print(f'Processing Car Type: {subsub_folder}')
            try:
                preprocess_cpam_data(sub_folder, subsub_folder, country_code)
            except Exception as e:
                logger.error(f'Error processing car type {subsub_folder}: {e}', extra={'country_code': country_code})
    logger.debug('CPAM data preprocessing completed', extra={'country_code': country_code})

def ingest_all_cpam_data(country_code, start_model_year=0):
    logger.info('Starting CPAM data update', extra={'country_code': country_code})
    folder = f"{os.getcwd()}/dist/cpam_data/{country_code}/"
    for sub_folder in os.listdir(folder):
        new_folder = folder + sub_folder + '/'
        if not os.path.isdir(new_folder) or int(sub_folder) < start_model_year:
            continue
        print(f'Ingesting Year: {sub_folder}')
        for subsub_folder in os.listdir(new_folder):
            if not os.path.isdir(new_folder + subsub_folder):
                continue
            print(f'Ingesting Car Type: {subsub_folder}')
            try:
                for _ in range(3):
                    try:
                        logger.info(f'Processing Car Type: {subsub_folder}')
                        ingest_cpam_data(sub_folder, subsub_folder, country_code)
                        break
                    except Exception as e:
                        logger.error(f'Failed to ingest data for {subsub_folder} in {sub_folder}: {e}')
                        raise e
                
                conditions = [f"CountryCode = '{country_code}'", f"ModelYear = '{sub_folder}'", f"CarType = '{subsub_folder}'"]
                df_raw = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), conditions=conditions)
                if df_raw is None or df_raw.empty:
                    continue
        
                df_processed = process_visa_df(df_raw)
                if df_processed is None or df_processed.empty:
                    continue
                
                df_processed.insert(7, 'CountryCode', country_code)
                ingest_visa_data(country_code, df_processed)
        
            except Exception as e:
                logger.error(f'Error ingesting car type {subsub_folder}: {e}', extra={'country_code': country_code})
    
    DBOperations.instance.consolidate_translations(country_code)
    logger.debug('CPAM data ingestion completed', extra={'country_code': country_code})

def fetch_cpam_data(year, car_type, country_code, sw):
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
    
    logger.info(f'Fetching data car type: {car_type} for year: {year}', extra={'country_code': country_code})
    global_dict_auth = utils.df_from_datarows(cpam.get_dictionary(year, car_type, country_code, '', sw).get('DataRows', None))
    market_dict_auth = utils.df_from_datarows(cpam.get_dictionary(year, car_type, country_code, 'm', sw).get('DataRows', None))
    
    if market_dict_auth.empty:
        logger.warn('No data found for the market', extra={'country_code': country_code})
        return
    
    global_authorization_auth = utils.df_from_datarows(cpam.get_authorization(year, car_type, country_code, '', sw).get('DataRows', None), ['Code', 'DataType'])
    market_authorization_auth = utils.df_from_datarows(cpam.get_authorization(year, car_type, country_code, 'm', sw).get('DataRows', None), ['Code', 'DataType'])
    authorized_pnos = market_authorization_auth[market_authorization_auth['DataType'] == 'PNO'].copy()
    
    authorized_packages = utils.df_from_package_datarows(cpam.get_packages(year, car_type, country_code, 'm', sw).get('PackageDataRows', None))
    
    global_dependency_auth = utils.df_from_datarows(cpam.get_dependency_rules(year, car_type, country_code, '', sw).get('DataRows', None), ['RuleCode', 'ItemCode', 'FeatureCode']).explode('FeatureCode')
    market_dependency_auth = utils.df_from_datarows(cpam.get_dependency_rules(year, car_type, country_code, 'm', sw).get('DataRows', None), ['RuleCode', 'ItemCode', 'FeatureCode']).explode('FeatureCode')
    
    global_feat_auth = utils.df_from_datarows(cpam.get_features(year, car_type, country_code, '', sw).get('DataRows', None), ['Code', 'Special', 'Reference'])
    market_feat_auth = utils.df_from_datarows(cpam.get_features(year, car_type, country_code, 'm', sw).get('DataRows', None), ['Code', 'Special', 'Reference'])
    
    folder = f"{os.getcwd()}/dist/cpam_data/{country_code}/{year}/{car_type}/raw"
    # Create the folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    ###############################################################################################################################################################################################################
    global_dict_auth.to_csv(f"{folder}/global_dict_auth.csv")
    market_dict_auth.to_csv(f"{folder}/market_dict_auth.csv")
    global_authorization_auth.to_csv(f"{folder}/global_authorization_auth.csv")
    market_authorization_auth.to_csv(f"{folder}/market_authorization_auth.csv")
    authorized_pnos.to_csv(f"{folder}/authorized_pnos.csv")
    authorized_packages.to_csv(f"{folder}/authorized_packages.csv")
    global_dependency_auth.to_csv(f"{folder}/global_dependency_auth.csv")
    market_dependency_auth.to_csv(f"{folder}/market_dependency_auth.csv")
    global_feat_auth.to_csv(f"{folder}/global_feat_auth.csv")
    market_feat_auth.to_csv(f"{folder}/market_feat_auth.csv")
    ###############################################################################################################################################################################################################
    
    logger.info(f'Data fetched for car type: {car_type} in year: {year} for country: {country_code}', extra={'country_code': country_code})

def preprocess_cpam_data(year, car_type, country_code):
    folder = f"{os.getcwd()}/dist/cpam_data/{country_code}/{year}/{car_type}/raw"
    if not os.path.exists(folder):
        logger.error(f'Folder {folder} does not exist', extra={'country_code': country_code})
        return
    
    def cast_start_and_enddate_to_int(df):
        if df.empty:
            return df
        df['StartDate'] = df['StartDate'].astype(int)
        df['EndDate'] = df['EndDate'].astype(int)
        return df
    
    ###############################################################################################################################################################################################################
    global_dict_auth = pd.read_csv(f"{folder}/global_dict_auth.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    market_dict_auth = pd.read_csv(f"{folder}/market_dict_auth.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    global_authorization_auth = pd.read_csv(f"{folder}/global_authorization_auth.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    market_authorization_auth = pd.read_csv(f"{folder}/market_authorization_auth.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    authorized_pnos = pd.read_csv(f"{folder}/authorized_pnos.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    authorized_packages = pd.read_csv(f"{folder}/authorized_packages.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    global_dependency_auth = pd.read_csv(f"{folder}/global_dependency_auth.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    market_dependency_auth = pd.read_csv(f"{folder}/market_dependency_auth.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    global_feat_auth = pd.read_csv(f"{folder}/global_feat_auth.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    market_feat_auth = pd.read_csv(f"{folder}/market_feat_auth.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).fillna('').reset_index(drop=True)
    ###############################################################################################################################################################################################################
    
    logger.info(f'Processing car type: {car_type} for year: {year} in folder: {folder}', extra={'country_code': country_code})
    authorized_dictionaries, unauthorized_dictionaries = get_authorization_status(global_dict_auth, market_dict_auth)
    authorized_authorizations, unauthorized_authorizations = get_authorization_status(global_authorization_auth, market_authorization_auth, authorized_pnos)
    authorized_dependencies, unauthorized_dependencies = get_authorization_status(global_dependency_auth, market_dependency_auth, authorized_pnos)
    authorized_features, unauthorized_features = get_authorization_status(global_feat_auth, market_feat_auth, authorized_pnos)
    
    folder = f"{os.getcwd()}/dist/cpam_data/{country_code}/{year}/{car_type}/processed"
    # Create the folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    ###############################################################################################################################################################################################################
    authorized_dictionaries.to_csv(f"{folder}/authorized_dictionaries.csv")
    unauthorized_dictionaries.to_csv(f"{folder}/unauthorized_dictionaries.csv")
    authorized_authorizations.to_csv(f"{folder}/authorized_authorizations.csv")
    unauthorized_authorizations.to_csv(f"{folder}/unauthorized_authorizations.csv")
    authorized_packages.to_csv(f"{folder}/authorized_packages.csv")
    authorized_dependencies.to_csv(f"{folder}/authorized_dependencies.csv")
    unauthorized_dependencies.to_csv(f"{folder}/unauthorized_dependencies.csv")
    # (de-)auth needs further discussions and work cause references have commas
    market_feat_auth.to_csv(f"{folder}/authorized_features.csv")
    unauthorized_features.to_csv(f"{folder}/unauthorized_features.csv")
    ###############################################################################################################################################################################################################
    
    logger.info(f'Data processed for car type: {car_type} in year: {year} for country: {country_code}', extra={'country_code': country_code})

def ingest_cpam_data(year, car_type, country_code):
    folder = f"{os.getcwd()}/dist/cpam_data/{country_code}/{year}/{car_type}/processed"
    if not os.path.exists(folder):
        logger.error(f'Folder {folder} does not exist', extra={'country_code': country_code})
        return
    def cast_start_and_enddate_to_int(df):
        if df.empty:
            return df
        df['StartDate'] = df['StartDate'].astype(int)
        df['EndDate'] = df['EndDate'].astype(int)
        return df
    ###############################################################################################################################################################################################################
    authorized_authorizations = pd.read_csv(f"{folder}/authorized_authorizations.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).reset_index(drop=True)
    authorized_dictionaries = pd.read_csv(f"{folder}/authorized_dictionaries.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).reset_index(drop=True)
    authorized_packages = pd.read_csv(f"{folder}/authorized_packages.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).reset_index(drop=True)
    authorized_dependencies = pd.read_csv(f"{folder}/authorized_dependencies.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).reset_index(drop=True)
    authorized_features = pd.read_csv(f"{folder}/authorized_features.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).reset_index(drop=True)
    unauthorized_authorizations = pd.read_csv(f"{folder}/unauthorized_authorizations.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).reset_index(drop=True)
    # unauthorized_dictionaries = pd.read_csv(f"{folder}/unauthorized_dictionaries.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).reset_index(drop=True)
    # unauthorized_dependencies = pd.read_csv(f"{folder}/unauthorized_dependencies.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).reset_index(drop=True)
    # unauthorized_features = pd.read_csv(f"{folder}/unauthorized_features.csv", index_col=0, dtype=str).pipe(cast_start_and_enddate_to_int).reset_index(drop=True)
    ###############################################################################################################################################################################################################
    
    if not authorized_dictionaries.empty:
        DBOperations.instance.collect_entity(authorized_dictionaries, country_code)
    if not unauthorized_authorizations.empty:
        DBOperations.instance.drop_auth(unauthorized_authorizations, country_code)
    if authorized_authorizations.empty:
        return
    df_pnos = DBOperations.instance.collect_auth(authorized_authorizations, country_code)
    # if df_pnos.empty:
    #     return
    # if not unauthorized_features.empty:
    #     DBOperations.instance.drop_feature(unauthorized_features, df_pnos)
    # # if not unauthorized_dependencies.empty:
    # #     DBOperations.instance.drop_dependency(unauthorized_dependencies, df_pnos)
    if not authorized_packages.empty:
        DBOperations.instance.collect_package(authorized_packages, df_pnos)
    if not authorized_dependencies.empty:
        DBOperations.instance.collect_dependency(authorized_dependencies, df_pnos)
    if not authorized_features.empty:
        DBOperations.instance.collect_feature(authorized_features, df_pnos)
    # # Don't drop entities because you might drop something used in a previously processed car type   
    # if not unauthorized_dictionaries.empty:
    #     DBOperations.instance.drop_entity(unauthorized_dictionaries, country_code)
    
    logger.info(f'Data insertion completed for car type: {car_type} in year: {year} for country: {country_code}', extra={'country_code': country_code})

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
