from flask import Blueprint, request, jsonify
import datetime

from src.ingest.cpam.services import fetch_all_cpam_data, ingest_all_cpam_data, process_all_cpam_data
from src.ingest.visa_files.services import ingest_visa_data, ingest_visa_file
from src.database.db_operations import DBOperations
from src.utils.sql_logging_handler import logger

# @author Hassan Wahba

bp_ingest = Blueprint('ingest', __name__, url_prefix='/api/<country>/ingest')

@bp_ingest.route('/cpam', methods=['GET'])
def refresh_all_cpam_data(country):
    logger.info('Refreshing CPAM Data')
    year = request.args.get('year', None)
    if year is None or not year.isdigit():
        logger.info('No year provided, refreshing current year and future years')
        this_week = datetime.datetime.now().isocalendar()[1]
        year = datetime.datetime.now().year
        if this_week > 16:
            year +=1
    max_tries = 3
    for i in range(max_tries):
        try:
            fetch_all_cpam_data(country, start_model_year=year)
            break
        except Exception as e:
            logger.error(f"Failed to fetch CPAM data: {e}", extra={'country': country})
            if i == max_tries - 1:
                break
    for i in range(max_tries):
        try:
            process_all_cpam_data(country, start_model_year=int(year))
            break
        except Exception as e:
            logger.error(f"Failed to process CPAM data: {e}", extra={'country': country})
            if i == max_tries - 1:
                break
    for i in range(max_tries):
        try:
            ingest_all_cpam_data(country, start_model_year=int(year))
            break
        except Exception as e:
            logger.error(f"Failed to ingest CPAM data: {e}", extra={'country': country})
            if i == max_tries - 1:
                break
    
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
