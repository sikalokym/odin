from flask import Blueprint, request, jsonify

from src.database.db_operations import DBOperations
from src.database.services import get_engine_cats
from src.utils.db_utils import filter_df_by_model_year


bp_db_manager = Blueprint('db_manager', __name__, url_prefix='/api/db/<country>/<model_year>')


@bp_db_manager.route('/engine_cats', methods=['GET'])
def retrieve_engine_cats(country, model_year):
    model = request.args.get('model')
    engine_cats = get_engine_cats(country, model_year, model)
    
    return jsonify(engine_cats)

@bp_db_manager.route('/pnos', methods=['GET'])
def get_pnos(country, model_year):
    columns = request.args.get('columns')
    if columns:
        columns = columns.split(',')
    else:
        columns = ['ID', 'Model', 'Engine', 'SalesVersion', 'Gearbox', 'StartDate', 'EndDate']

    if model_year == '0':
        return jsonify([])

    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), columns, conditions=[f'CountryCode = {country}'])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    
    return df_pnos.to_json(orient='records')

@bp_db_manager.route('/models', methods=['GET'])
def get_models(country, model_year):
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['Model', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    
    df_models = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'Typ'), columns=['Code', 'MarketText'], conditions=[f'CountryCode = {country}'])
    df_models = df_models[df_models['Code'].isin(df_pnos['Model'])]

    return df_models.to_json(orient='records')
