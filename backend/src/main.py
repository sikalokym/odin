from dotenv import load_dotenv
from zipfile import ZipFile
import pandas as pd
import datetime
import time
import os

from src.ingest.cpam.services import fetch_all_cpam_data, fetch_cpam_data, get_supported_countries, ingest_all_cpam_data, ingest_cpam_data, process_all_cpam_data
from src.export.variant_binder import _extract_variant_binder, extract_variant_binder, extract_variant_binder_pnos
from src.utils.scheduler import schedule_fetch_task, schedule_ingest_task
from src.export.sap_price_list import extract_sap_price_list
from src.ingest.visa_files.services import ingest_visa_data
from src.routes.ingest_routes import refresh_all_cpam_data
from src.database.db_operations import DBOperations
from src.utils.sql_logging_handler import logger
from src.ingest.visa_files import preprocess
import src.utils.db_utils as utils

# @author Hassan Wahba

# Load environment variables
load_dotenv(override=True)
DBOperations.create_instance(logger=logger)

if __name__ == "__main__":
    current_time = pd.Timestamp.now()
    country = '231'
    
    #### refresh all visa file prices for a country
    # conditions = [f"CountryCode = '{country}'", f"ModelYear = '2025'", f"CarType = '246'"]
    # df_raw = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), conditions=conditions)
    # df_processed = preprocess.process_visa_df(df_raw)
    # df_processed.insert(7, 'CountryCode', country)
    # ingest_visa_data(country, df_processed)
    # ingest_visa_data(country, None)
    # ingest_all_cpam_data(country)
    # ingest_all_cpam_data(country, start_model_year=2024)
    # ingest_cpam_data(2025, '246', country)
    
    #### extract variant binders of many car types in a country
    # _extract_variant_binder(country, '539', "All", 202502)
    # _extract_variant_binder(country, '246', "All", 202422)
    # _extract_variant_binder(country, '246', "Plug-in Hybrid", 202423)
    # _extract_variant_binder(country, '235', "Plug-in Hybrid", 202418)
    
    #### fetch, process and ingest all cpam data for a country
    # fetch_all_cpam_data(country, start_model_year=2021)
    # fetch_cpam_data(2024, '246', country, '')
    # print(f'Execution time: {pd.Timestamp.now() - current_time}')
    # process_all_cpam_data(country, 2021)
    # print(f'Execution time: {pd.Timestamp.now() - current_time}')
    
    #### consolidate translations though all available years for a country
    # DBOperations.instance.consolidate_translations(country)
    
    #### extract sap price list for a country given a sales channel and a model year
    # zip_buffer = extract_sap_price_list(country, 'All', None, '2025')
    # with ZipFile(zip_buffer) as zf:
    #     zf.extractall('dist/sap_price_list_main_test')
    # schedule_ingest_task()
    print(f'Execution time: {pd.Timestamp.now() - current_time}')
