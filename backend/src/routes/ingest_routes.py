from flask import Blueprint, request, jsonify

from src.ingest.cpam.services import ingest_all_cpam_data, ingest_cpam_data
from src.ingest.visa_files.services import upload_visa_file, ingest_visa_data
from src.utils.ingest_utils import is_valid_car_type, is_valid_year

bp_ingest = Blueprint('ingest', __name__, url_prefix='/api/<country>/ingest')


@bp_ingest.route('/cpam', methods=['GET'])
def refresh_all_cpam_data(country):
    load_successfull, load_unsuccessfull = ingest_all_cpam_data(country)
    return jsonify({'success': load_successfull, 'failed': load_unsuccessfull})

@bp_ingest.route('/cpam/<year>/<car_type>', methods=['GET'])
def refresh_cpam_data(country, year, car_type):
    
    is_valid = is_valid_year(year, country)
    if isinstance(is_valid, str):
        return jsonify({'error': is_valid}), 500
    if not is_valid:
        return jsonify({'error': 'Invalid year'}), 400
    
    if not is_valid_car_type(car_type, year, country):
        return jsonify({'error': 'Invalid car type'}), 400
    try:
        ingest_cpam_data(year, car_type, country, 'M', '')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp_ingest.route('/visa', methods=['GET'])
def refresh_visa_data(country):
    ingest_visa_data(country)

@bp_ingest.route('/visa/upload', methods=['POST'])
def new_visa_file(country):
    visa = request.files['visa']
    if visa.content_type not in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        return jsonify({'error': 'Invalid file type. Only Excel files are allowed.'}), 400
    
    if visa.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    res, code = upload_visa_file(visa, country)
    return jsonify(res), code
