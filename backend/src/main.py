import datetime
import io
import logging
import zipfile
import pandas as pd
from dotenv import load_dotenv

from src.database.db_operations import DBOperations
from src.export.sap_price_list import get_sap_price_list
from src.export.variant_binder import extract_variant_binder
from src.ingest.cpam.services import ingest_cpam_data
from src.storage.blob import load_available_visa_files, load_visa_files

# Load environment variables
load_dotenv(override=True)
DBOperations.create_instance()

# Logger configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Get the current timestamp
    current_time = pd.Timestamp.now()
    ingest_cpam_data('2023', '256', '231', 'M', '')
    end_time = pd.Timestamp.now()
    duration = end_time - current_time
    logger.info(f'Execution time: {duration}')
    print('Execution time: ', duration)

def do_extract(country):
    curr_time = 202430
    extract_variant_binder(country, '246', "Mild Hybrid", curr_time)

def sap_price_list(country, data):
    code = data.get('code', 'All')
    if code != 'All':
        conditions = [f'CountryCode = {country}', f"Code = '{code}'"]
        df_code_exists = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'CP'), columns=['Code', 'PartnerName', 'Discount', 'Comment', 'StartDate', 'EndDate'], conditions=conditions)
        if df_code_exists.empty:
            return 'Invalid code', 400

    visa_file = data['visa_file']
    visa_files = load_available_visa_files(country)
    if visa_file not in visa_files and visa_file != 'All':
        return 'Invalid visa file', 400
    time = datetime.datetime.now().strftime("%Y%U")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        if visa_file == 'All':
            for folder_name, blob in visa_files.items():
                dfs = get_sap_price_list(blob, code, country, time)
                concatenated_df = pd.concat(dfs)

                for df in dfs:
                    partner_code, partner_name = df.name.split('+#+')
                    excel_filename = f'SAP - PL{partner_code} - {partner_name}.xlsx'
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    zip_file.writestr(f'{folder_name}/{excel_filename}', excel_buffer.getvalue())

                concat_excel_buffer = io.BytesIO()
                with pd.ExcelWriter(concat_excel_buffer, engine='openpyxl') as writer:
                    concatenated_df.to_excel(writer, index=False)
                zip_file.writestr(f'{folder_name}/MAWISTA ALL.xlsx', concat_excel_buffer.getvalue())
        else:
            dfs = get_sap_price_list(visa_files[visa_file], code, country, time)
            concatenated_df = pd.concat(dfs)
            for df in dfs:
                code, partner_name = df.name.split('+#+')
                excel_filename = f'SAP - PL{code} - {partner_name}.xlsx'
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                zip_file.writestr(excel_filename, excel_buffer.getvalue())

    with open('sap_price_list_test_2.zip', 'wb') as f:
        f.write(zip_buffer.getvalue())

if __name__ == "__main__":
    # ingest_all_cpam_data('231', start_model_year='2021')
    # ingest_cpam_data('2024', '246', '231', 'M', '')
    # do_extract('231')
    # print(load_visa_files('231'))
    # sap_price_list('231', {'visa_file': 'All', 'code': 'All'})
    # sap_price_list('231', {'visa_file': 'VISA2PCTF - Germany XC90 MY25_24w17 (23w35)', 'code': '1'})
    sap_price_list('231', {'visa_file': 'All', 'code': 'All'})
