import logging
import pandas as pd
from dotenv import load_dotenv

from src.database.db_operations import DBOperations
from src.export.variant_binder import extract_variant_binder
from src.ingest.cpam.services import ingest_cpam_data

# Load environment variables
load_dotenv(override=True)
DBOperations.create_instance()

# Logger configuration
logging.basicConfig(level=20, format='%(asctime)s - %(levelname)s - %(message)s', filename='logs/app.log')
logger = logging.getLogger(__name__)

def main():
    # Get the current timestamp
    current_time = pd.Timestamp.now()
    ingest_cpam_data('2023', '256', '231', 'M', '')
    end_time = pd.Timestamp.now()
    duration = end_time - current_time
    logger.info(f'Execution time: {duration}')
    print('Execution time: ', duration)

def do_extract():
    # Get the current timestamp
    current_time = pd.Timestamp.now()
    formatted_time = current_time.strftime('%Y%U')

    # Convert the formatted string to an integer
    curr_time = int(formatted_time)
    curr_time = 202430
    country = '231'
    extract_variant_binder(country, '246', "ALL", curr_time)
    extract_variant_binder(country, '246', "Plug-in Hybrid", curr_time)
    extract_variant_binder(country, '256', "Plug-in Hybrid", curr_time)
    extract_variant_binder(country, '539', "", curr_time)

if __name__ == "__main__":
    # ingest_all_cpam_data('231', start_model_year='2021')
    do_extract()
