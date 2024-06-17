from flask import Blueprint, jsonify

from src.database.db_operations import DBOperations
from src.ingest.cpam.services import get_supported_countries
from src.utils.db_utils import get_model_year_from_date


bp_settings = Blueprint('settings', __name__, url_prefix='/api/setup')

@bp_settings.route('/<country>/available_model_years', methods=['GET'])
def get_available_model_years(country):
    pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), columns=['StartDate'], conditions=[f"CountryCode = '{country}'"])
    model_years = sorted(pnos['StartDate'].apply(get_model_year_from_date).unique().tolist())
    
    return jsonify(model_years)

@bp_settings.route('/supported_countries', methods=['GET'])
def fetch_supported_countries():
    countries = get_supported_countries()
    countries = countries.to_dict(orient='records')

    return jsonify(countries)
