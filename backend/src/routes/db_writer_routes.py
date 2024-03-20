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
    if not isinstance(data, list):
        data = [data]
    df = pd.DataFrame(data)
    df_engines = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'En'), conditions=[f'CountryCode = {country}'])
    update_columns = ['CountryText', 'Performance', 'EngineCategory', 'EngineType']

    # Update the columns in the df_engines DataFrame
    for col in update_columns:
        df_engines.loc[df_engines['Code'].isin(df['Code']), col] = df[col]


    all_columns = df_engines.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_engines, DBOperations.instance.config.get('TABLES', 'En'), all_columns, conditional_columns)
    return jsonify({'message': 'Engines written successfully'}), 200
