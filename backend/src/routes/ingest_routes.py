import datetime
import os
from flask import Blueprint, request, jsonify

from src.ingest.visa_files.preprocess import process_visa_df
from src.database.db_operations import DBOperations
from src.utils.sql_logging_handler import logger
from src.ingest.cpam.services import ingest_all_cpam_data, ingest_cpam_data
from src.ingest.visa_files.services import ingest_visa_data, ingest_visa_file
from src.utils.ingest_utils import is_valid_car_type, is_valid_year

bp_ingest = Blueprint('ingest', __name__, url_prefix='/api/<country>/ingest')


@bp_ingest.route('/cpam', methods=['GET'])
def refresh_all_cpam_data(country):
    logger.info('Refreshing CPAM Data')
    year= request.args.get('year', None)
    if year is None or not year.isdigit():
        logger.info('No year provided, refreshing current year and future years')
        this_week = datetime.datetime.now().isocalendar()[1]
        year = datetime.datetime.now().year
        if this_week > 16:
            year +=1
    folder = f"{os.getcwd()}/dist/cpam_data/231/"
    for sub_folder in os.listdir(folder):
        if int(sub_folder) < int(year):
            continue
        new_folder = folder + sub_folder + '/'
        if not os.path.isdir(new_folder):
            continue
        logger.info(f'Processing Year: {sub_folder}')
        for subsub_folder in os.listdir(new_folder):
            if not os.path.isdir(new_folder + subsub_folder):
                continue
            for _ in range(3):
                try:
                    logger.info(f'Processing Car Type: {subsub_folder}')
                    ingest_cpam_data(sub_folder, subsub_folder, '231')
                    break
                except Exception as e:
                    logger.error(f'Failed to ingest data for {subsub_folder} in {sub_folder}: {e}')
    
            conditions = [f"CountryCode = '{country}'", f"ModelYear = '{sub_folder}'", f"CarType = '{subsub_folder}'"]
            df_raw = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), conditions=conditions)
            if df_raw is None or df_raw.empty:
                continue
    
            df_processed = process_visa_df(df_raw)
            if df_processed is None or df_processed.empty:
                continue
            
            df_processed.insert(7, 'CountryCode', country)
            ingest_visa_data(country, df_processed)
    
    DBOperations.instance.consolidate_translations(country)
    DBOperations.instance.logger.info('CPAM Data Refreshed', extra={'country': country})
    return 'Ingestion Over', 200

@bp_ingest.route('/visa', methods=['GET'])
def refresh_visa_data(country):
    ingest_visa_data(country, None)

@bp_ingest.route('/visa/upload', methods=['POST'])
def new_visa_file(country):
    visa = request.files.get('visa', None)
    if visa is None:
        return jsonify({'error': 'No file part'}), 400
    if visa.content_type not in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        return jsonify({'error': 'Invalid file type. Only Excel files are allowed.'}), 400
    
    if visa.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    res, code = ingest_visa_file(visa, country)
    return jsonify(res), code
