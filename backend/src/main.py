import pandas as pd
from dotenv import load_dotenv

from src.database.db_operations import DBOperations
from src.export.sap_price_list import extract_sap_price_list
from src.export.variant_binder import extract_variant_binder, extract_variant_binder_pnos
from src.ingest.cpam.services import ingest_all_cpam_data, ingest_cpam_data
from src.ingest.visa_files.services import ingest_visa_data
from src.utils.sql_logging_handler import logger

# Load environment variables
load_dotenv(override=True)
DBOperations.create_instance(test=0, logger=logger)

def main():
    # Get the current timestamp
    current_time = pd.Timestamp.now()
    ingest_cpam_data('2023', '256', '231', 'M', '')
    end_time = pd.Timestamp.now()
    duration = end_time - current_time
    logger.info(f'Execution time: {duration}')
    print('Execution time: ', duration)

if __name__ == "__main__":
    # ingest_visa_data('231', None)
    # ingest_all_cpam_data('231', year='2025', start_model_year='2021')
    # ingest_cpam_data('2024', '246', '231', 'M', '')
    # extract_variant_binder('231', '246', "Mild Hybrid", 202430)
    # extract_sap_price_list('231', 'All', '2024-03-30')
    main()
