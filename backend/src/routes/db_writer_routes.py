from flask import Blueprint, request, jsonify
import pandas as pd

from src.database.db_operations import DBOperations


bp_db_writer = Blueprint('db_writer', __name__, url_prefix='/api/db/<country>/<model_year>/write')
    
@bp_db_writer.route('/engines', methods=['POST'])
def write_engines(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Create a DataFrame from the list of JSON objects
    df = pd.DataFrame(data)
    df_engines = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'En'), conditions=[f'CountryCode = {country}'])
    columns_to_update = ['CountryText', 'Performance', 'EngineCategory', 'EngineType']
    new_column_names = ['country_text', 'performance', 'engine_category', 'engine_type']

    for old_col, new_col in zip(columns_to_update, new_column_names):
        df_engines.loc[df_engines['Code'].isin(df['Code']), old_col] = df[new_col]

    all_columns = df_engines.columns.tolist()
    conditional_columns = list(set(all_columns) - set(columns_to_update))

    DBOperations.instance.upsert_data_from_df(df_engines, DBOperations.instance.config.get('TABLES', 'En'), all_columns, conditional_columns)
    return jsonify({'message': 'Engines written successfully'}), 200
