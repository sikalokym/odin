import datetime
from zipfile import ZipFile
import pandas as pd
from dotenv import load_dotenv

from src.routes.ingest_routes import refresh_all_cpam_data
import src.utils.db_utils as utils
from src.database.db_operations import DBOperations
from src.export.sap_price_list import extract_sap_price_list
from src.export.variant_binder import _extract_variant_binder, extract_variant_binder_pnos
from src.ingest.cpam.services import ingest_all_cpam_data, ingest_cpam_data
from src.ingest.visa_files.services import ingest_visa_data
from src.ingest.visa_files import preprocess
from src.utils.scheduler import scheduled_task
from src.utils.sql_logging_handler import logger

# Load environment variables
load_dotenv(override=True)
DBOperations.create_instance(test=0, logger=logger)

def main():
    # Get the current timestamp
    current_time = pd.Timestamp.now()
    ingest_all_cpam_data('231', start_model_year='2025')
    # ingest_cpam_data('2023', '246', '231', 'M', '')
    end_time = pd.Timestamp.now()
    duration = end_time - current_time
    logger.info(f'Execution time: {duration}')
    print('Execution time: ', duration)

if __name__ == "__main__":
    current_time = pd.Timestamp.now()
    # ingest_all_cpam_data('231', year='', start_model_year='2022')
    # ingest_all_cpam_data('231', year='2021')
    # scheduled_task()
    ingest_cpam_data('2026', '235', '231', '')
    # ingest_cpam_data('2024', '534', '231', '')
    # import os
    # this_week = datetime.datetime.now().isocalendar()[1]
    # year = datetime.datetime.now().year
    # if this_week > 16:
    #     year +=1
    # folder = f"{os.getcwd()}/dist/cpam_data/231/"
    # for sub_folder in os.listdir(folder):
    #     if sub_folder < year:
    #         continue
    #     new_folder = folder + sub_folder + '/'
    #     if not os.path.isdir(new_folder):
    #         continue
    #     print(f'Processing Year: {sub_folder}')
    #     for subsub_folder in os.listdir(new_folder):
    #         if not os.path.isdir(new_folder + subsub_folder):
    #             continue
    #         print(f'Processing Car Type: {subsub_folder}')
    #         print(sub_folder, subsub_folder, '231', '')
    # refresh_all_cpam_data('231')
    # ingest_cpam_data('2022', '246', '231', '')
    # ingest_cpam_data('2024', '246', '231', '')
    # ingest_cpam_data('2025', '246', '231', '')
    # ingest_cpam_data('2026', '246', '231', '')
    # conditions = [f"CountryCode = '231'", f"ModelYear = '2025'", f"CarType = '246'"]
    # df_raw = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), conditions=conditions)
    # df_processed = preprocess.process_visa_df(df_raw)
    # df_processed.insert(7, 'CountryCode', '231')
    # ingest_visa_data('231', df_processed)
    # _extract_variant_binder('231', '246', "All", 202521)
    # main()
    # DBOperations.instance.consolidate_translations('231')
    # zip_buffer = extract_sap_price_list('231', 'All', None, '2025')
    # with ZipFile(zip_buffer) as zf:
    #     zf.extractall('dist/sap_price_list_main_test')
    print(f'Execution time: {pd.Timestamp.now() - current_time}')
