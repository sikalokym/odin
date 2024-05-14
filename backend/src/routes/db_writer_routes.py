from flask import Blueprint, request, jsonify
import pandas as pd
import random
import numpy as np

from src.database.db_operations import DBOperations
from src.utils.db_utils import filter_df_by_model_year


bp_db_writer = Blueprint('db_writer', __name__, url_prefix='/api/db/<country>/<model_year>/write')

@bp_db_writer.route('/models', methods=['POST'])
def write_models(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Create a DataFrame from the list of JSON objects
    df_models = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'Typ'), conditions=[f'CountryCode = {country}'])
    update_columns = ['CustomName']

    # Update the columns in the df_models DataFrame
    for col in update_columns:
        df_models.loc[df_models['Code'] == data['Code'], col] = data[col]
    all_columns = df_models.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_models, DBOperations.instance.config.get('TABLES', 'Typ'), all_columns, conditional_columns)
    return jsonify({'message': 'Models written successfully'}), 200

@bp_db_writer.route('/engines', methods=['POST'])
def write_engines(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Create a DataFrame from the list of JSON objects
    df_engines = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'En'), conditions=[f'CountryCode = {country}'])
    update_columns = ['CustomName', 'Performance', 'EngineCategory', 'EngineType']

    # Update the columns in the df_engines DataFrame
    for col in update_columns:
        df_engines.loc[df_engines['Code'] == data['Code'], col] = data[col]
    all_columns = df_engines.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_engines, DBOperations.instance.config.get('TABLES', 'En'), all_columns, conditional_columns)
    return jsonify({'message': 'Engines written successfully'}), 200
    
@bp_db_writer.route('/sales_versions', methods=['POST'])
def write_sales_versions(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Create a DataFrame from the list of JSON objects
    df_sales_versions = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'SV'), conditions=[f'CountryCode = {country}'])
    update_columns = ['CustomName']

    # Update the columns in the df_sales_versions DataFrame
    for col in update_columns:
        df_sales_versions.loc[df_sales_versions['Code'] == data['Code'], col] = data[col]
    all_columns = df_sales_versions.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_sales_versions, DBOperations.instance.config.get('TABLES', 'SV'), all_columns, conditional_columns)
    return jsonify({'message': 'Sales Versions written successfully'}), 200

@bp_db_writer.route('/gearboxes', methods=['POST'])
def write_gearboxes(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Create a DataFrame from the list of JSON objects
    df_gearboxes = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'G'), conditions=[f'CountryCode = {country}'])
    update_columns = ['CustomName']

    # Update the columns in the df_gearboxes DataFrame
    for col in update_columns:
        df_gearboxes.loc[df_gearboxes['Code'] == data['Code'], col] = data[col]
    all_columns = df_gearboxes.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_gearboxes, DBOperations.instance.config.get('TABLES', 'G'), all_columns, conditional_columns)
    return jsonify({'message': 'Gearboxes written successfully'}), 200

@bp_db_writer.route('/features', methods=['POST'])
def write_features(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data['Code']

    model = data.get('Model', None)
    pnos_conditions = [f'CountryCode = {country}']
    if model:
        pnos_conditions.append(f"Model = '{model}'")

    # Create a DataFrame from the list of JSON objects
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=pnos_conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    ids = df_pnos['ID'].tolist()
    conditions = [f"Code = '{code}'"]
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    table = DBOperations.instance.config.get('AUTH', 'CFEAT') if data.get('Custom') else DBOperations.instance.config.get('AUTH', 'FEAT')
    df_pno_features = DBOperations.instance.get_table_df(table, conditions=conditions)
    update_columns = ['CustomName', 'CustomCategory']

    # Update the columns in the df_pno_features DataFrame
    for col in update_columns:
        df_pno_features[col] = data[col]
    all_columns = df_pno_features.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_pno_features, table, all_columns, conditional_columns)
    return jsonify({'message': 'Features written successfully'}), 200

@bp_db_writer.route('/update/customfeatures', methods=['POST'])
def update_customfeatures(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    model = data.get('Model', None)
    pnos_conditions = [f'CountryCode = {country}']
    if model:
        pnos_conditions.append(f"Model = '{model}'")


    # Create a DataFrame from the list of JSON objects
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=pnos_conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    ids = df_pnos['ID'].tolist()
    code = data.get('Code', None)
    if code is None:
        return jsonify({'error': 'No code provided'}), 400

    conditions = [f"Code = '{code}'"]
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_pno_custom_features = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'CFEAT'), conditions=conditions)

    update_columns = ['CustomName', 'CustomCategory']

    # Update the columns in the df_pno_features DataFrame
    for col in update_columns:
        df_pno_custom_features[col] = data[col]

    all_columns = df_pno_custom_features.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_pno_custom_features, DBOperations.instance.config.get('AUTH', 'CFEAT'), all_columns, conditional_columns)
    return jsonify({'message': 'Features written successfully'}), 200


@bp_db_writer.route('/insert/customfeatures', methods=['POST'])
def write_customfeatures(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    model = data['Model']

    # Create a DataFrame from the list of JSON objects
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}', f"Model = '{model}'"])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    ids = df_pnos['ID'].tolist()

    df_pno_custom_features_old = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'CFEAT'))

    if df_pno_custom_features_old.empty:
        custom_code = 'XY0001'
    else:
        codes = df_pno_custom_features_old['Code'].unique().tolist()
        leading_digits = [int(code[-4:]) for code in codes]
        custom_code = f'XY{str(max(leading_digits) + 1).zfill(4)}'
        
    rows = []
    for id in ids:
        new_row = {'PNOID': id, 'Code': custom_code, 'CustomName': data['CustomName'], 'CustomCategory': data['CustomCategory'], 'StartDate': data['StartDate'], 'EndDate': data['EndDate']}
        rows.append(new_row)
    df_pno_custom_features_new = pd.DataFrame(rows)
    all_columns = df_pno_custom_features_new.columns.tolist()
    DBOperations.instance.upsert_data_from_df(df_pno_custom_features_new, DBOperations.instance.config.get('AUTH', 'CFEAT'), all_columns, ['PNOID', 'Code'])
    return jsonify({'message': 'Features written successfully'}), 200

@bp_db_writer.route('/options', methods=['POST'])
def write_options(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data['Code']

    model = data.get('Model', None)
    pnos_conditions = [f'CountryCode = {country}']
    if model:
        pnos_conditions.append(f"Model = '{model}'")

    # Create a DataFrame from the list of JSON objects
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=pnos_conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    ids = df_pnos['ID'].tolist()
    conditions = [f"Code = '{code}'"]
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_pno_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'OPT'), conditions=conditions)
    df_pno_options['CustomName'] = data['CustomName']

    df_pno_options_relations = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'OPT_Custom'))

    df_pno_options_relations = df_pno_options_relations[df_pno_options_relations['RelationID'].isin(df_pno_options['ID'])]

    update_columns = ['CustomName']

    # Update the columns in the df_pno_options_relation DataFrame
    for col in update_columns:
        df_pno_options_relations[col] = data[col]
    all_columns = df_pno_options_relations.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_pno_options_relations, DBOperations.instance.config.get('RELATIONS', 'OPT_Custom'), all_columns, conditional_columns)
    return jsonify({'message': 'Options written successfully'}), 200

@bp_db_writer.route('/colors', methods=['POST'])
def write_colors(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data['Code']

    model = data.get('Model', None)
    pnos_conditions = [f'CountryCode = {country}']
    if model:
        pnos_conditions.append(f"Model = '{model}'")

    # Create a DataFrame from the list of JSON objects
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=pnos_conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    ids = df_pnos['ID'].tolist()
    conditions = [f"Code = '{code}'"]
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_pno_colors = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'COL'), conditions=conditions)
    df_pno_colors['CustomName'] = data['CustomName']

    df_pno_colors_relations = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'COL_Custom'))

    df_pno_colors_relations = df_pno_colors_relations[df_pno_colors_relations['RelationID'].isin(df_pno_colors['ID'])]

    update_columns = ['CustomName']

    # Update the columns in the df_pno_colors_relation DataFrame
    for col in update_columns:
        df_pno_colors_relations[col] = data[col]
    all_columns = df_pno_colors_relations.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_pno_colors_relations, DBOperations.instance.config.get('RELATIONS', 'COL_Custom'), all_columns, conditional_columns)
    return jsonify({'message': 'Colors written successfully'}), 200

@bp_db_writer.route('/upholstery', methods=['POST'])
def write_upholstery(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data['Code']

    model = data.get('Model', None)
    pnos_conditions = [f'CountryCode = {country}']
    if model:
        pnos_conditions.append(f"Model = '{model}'")

    # Create a DataFrame from the list of JSON objects
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=pnos_conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    ids = df_pnos['ID'].tolist()
    conditions = [f"Code = '{code}'"]
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_pno_upholstery = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'UPH'), conditions=conditions)
    rel_ids = df_pno_upholstery['ID'].unique().tolist()
    uph_conditions = []
    if len(rel_ids) == 1:
        uph_conditions.append(f"RelationID = '{rel_ids[0]}'")
    else:
        uph_conditions.append(f"RelationID in {tuple(rel_ids)}")

    df_pno_upholstery_relations = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'UPH_Custom'), conditions=uph_conditions)

    update_columns = ['CustomName'] # ['CustomName', 'CustomCategory']

    # Update the columns in the df_pno_upholstery_relation DataFrame
    for col in update_columns:
        df_pno_upholstery_relations[col] = data[col]
    all_columns = df_pno_upholstery_relations.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_pno_upholstery_relations, DBOperations.instance.config.get('RELATIONS', 'UPH_Custom'), all_columns, conditional_columns)
    return jsonify({'message': 'Upholstery written successfully'}), 200

@bp_db_writer.route('/packages', methods=['POST'])
def write_packages(country, model_year):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    model = data.get('Model', None)
    pnos_conditions = [f'CountryCode = {country}']
    if model:
        pnos_conditions.append(f"Model = '{model}'")
    # Create a DataFrame from the list of JSON objects
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=pnos_conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    ids = df_pnos['ID'].tolist()
    code = data['Code']
    conditions = [f"Code = '{code}'"]
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_pno_packages = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PKG'), ['ID'], conditions=conditions)
    
    rel_ids = df_pno_packages['ID'].unique().tolist()
    package_conditions = []
    if len(rel_ids) == 1:
        package_conditions.append(f"RelationID = '{rel_ids[0]}'")
    else:
        package_conditions.append(f"RelationID in {tuple(rel_ids)}")

    df_pno_packages_relations = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'PKG_Custom'), columns=['RelationID', 'CustomName'], conditions=package_conditions)

    update_columns = ['CustomName']

    # Update the columns in the df_pno_packages_relation DataFrame
    for col in update_columns:
        df_pno_packages_relations[col] = data[col]
    all_columns = df_pno_packages_relations.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_pno_packages_relations, DBOperations.instance.config.get('RELATIONS', 'PKG_Custom'), all_columns, conditional_columns)
    return jsonify({'message': 'Packages written successfully'}), 200