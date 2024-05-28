import uuid
from flask import Blueprint, request
import pandas as pd

from src.database.db_operations import DBOperations
from src.utils.db_utils import filter_df_by_model_year


bp_db_writer = Blueprint('db_writer', __name__, url_prefix='/api/db/<country>/<model_year>/write')

@bp_db_writer.route('/models', methods=['POST'])
def write_models(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
    # Create a DataFrame from the list of JSON objects
    df_models = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'Typ'), conditions=[f'CountryCode = {country}'])
    df_models = filter_df_by_model_year(df_models, model_year)
    update_columns = ['CustomName']

    # Update the columns in the df_models DataFrame
    for col in update_columns:
        df_models.loc[df_models['Code'] == data['Code'], col] = data[col]
    all_columns = df_models.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_models, DBOperations.instance.config.get('TABLES', 'Typ'), all_columns, conditional_columns)
    return 'Models written successfully', 200

@bp_db_writer.route('/engines', methods=['POST'])
def write_engines(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
    # Create a DataFrame from the list of JSON objects
    df_engines = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'En'), conditions=[f'CountryCode = {country}'])
    df_engines = filter_df_by_model_year(df_engines, model_year)
    update_columns = ['CustomName', 'Performance', 'EngineCategory', 'EngineType']

    # Update the columns in the df_engines DataFrame
    for col in update_columns:
        df_engines.loc[df_engines['Code'] == data['Code'], col] = data[col]
    all_columns = df_engines.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_engines, DBOperations.instance.config.get('TABLES', 'En'), all_columns, conditional_columns)
    return 'Engines written successfully', 200
    
@bp_db_writer.route('/sales_versions', methods=['POST'])
def write_sales_versions(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
    # Create a DataFrame from the list of JSON objects
    df_sales_versions = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'SV'), conditions=[f'CountryCode = {country}'])
    df_sales_versions = filter_df_by_model_year(df_sales_versions, model_year)
    update_columns = ['CustomName']

    # Update the columns in the df_sales_versions DataFrame
    for col in update_columns:
        df_sales_versions.loc[df_sales_versions['Code'] == data['Code'], col] = data[col]
    all_columns = df_sales_versions.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_sales_versions, DBOperations.instance.config.get('TABLES', 'SV'), all_columns, conditional_columns)
    return 'Sales Versions written successfully', 200

@bp_db_writer.route('/gearboxes', methods=['POST'])
def write_gearboxes(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
    # Create a DataFrame from the list of JSON objects
    df_gearboxes = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'G'), conditions=[f'CountryCode = {country}'])
    df_gearboxes = filter_df_by_model_year(df_gearboxes, model_year)
    update_columns = ['CustomName']

    # Update the columns in the df_gearboxes DataFrame
    for col in update_columns:
        df_gearboxes.loc[df_gearboxes['Code'] == data['Code'], col] = data[col]
    all_columns = df_gearboxes.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_gearboxes, DBOperations.instance.config.get('TABLES', 'G'), all_columns, conditional_columns)
    return 'Gearboxes written successfully', 200

@bp_db_writer.route('/features', methods=['POST'])
def write_features(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
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
    return 'Features written successfully', 200

@bp_db_writer.route('/update/customfeatures', methods=['POST'])
def update_customfeatures(country, model_year):
    data = request.get_json()
    ids = data.get('ID', None)
    if ids is None:
        return 'No ID provided', 400
    ids = ids.split(',')
    conditions = []
    if len(ids) == 1:
        conditions.append(f"ID = '{ids[0]}'")
    else:
        conditions.append(f"ID in {tuple(ids)}")
    df_pno_custom_features = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'CFEAT'), conditions=conditions)

    update_columns = ['CustomName', 'CustomCategory']

    # Update the columns in the df_pno_features DataFrame
    for col in update_columns:
        df_pno_custom_features[col] = data[col]

    all_columns = df_pno_custom_features.columns.tolist()
    conditional_columns = ['ID']

    DBOperations.instance.upsert_data_from_df(df_pno_custom_features, DBOperations.instance.config.get('AUTH', 'CFEAT'), all_columns, conditional_columns)
    return 'Features written successfully', 200

@bp_db_writer.route('/insert/customfeatures', methods=['POST'])
def write_customfeatures(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
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
    return 'Features written successfully', 200

@bp_db_writer.route('/delete/customfeatures', methods=['POST'])
def delete_customfeatures(country, model_year):
    ids = request.args.get('ID')
    if not ids:
        return {"error": "ID is required"}, 400
    
    table_name = DBOperations.instance.config.get('AUTH', 'CFEAT')

    # Construct the DELETE query
    delete_query = f"DELETE FROM {table_name} WHERE ID IN ?"

    try:
        with DBOperations.instance.get_cursor() as cursor:
            cursor.execute(delete_query, (tuple(ids.split(',')),))
        return {"message": "Records deleted successfully"}, 200
    except Exception as e:
        DBOperations.instance.logger.error(f"Error deleting records: {e}")
        return {"error": str(e)}, 500

@bp_db_writer.route('/options', methods=['POST'])
def write_options(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
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
    rel_ids = df_pno_options['ID'].tolist()
    options_conditions = []
    if len(rel_ids) == 1:
        options_conditions.append(f"RelationID = '{rel_ids[0]}'")
    else:
        options_conditions.append(f"RelationID in {tuple(rel_ids)}")

    df_pno_options_relations = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'OPT_Custom'), conditions=options_conditions)

    update_columns = ['CustomName']

    # Update the columns in the df_pno_options_relation DataFrame
    for col in update_columns:
        df_pno_options_relations[col] = data[col]
    all_columns = df_pno_options_relations.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_pno_options_relations, DBOperations.instance.config.get('RELATIONS', 'OPT_Custom'), all_columns, conditional_columns)
    return 'Options written successfully', 200

@bp_db_writer.route('/colors', methods=['POST'])
def write_colors(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
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
    rel_ids = df_pno_colors['ID'].tolist()
    colors_conditions = []
    if len(rel_ids) == 1:
        colors_conditions.append(f"RelationID = '{rel_ids[0]}'")
    else:
        colors_conditions.append(f"RelationID in {tuple(rel_ids)}")

    df_pno_colors_relations = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'COL_Custom'), conditions=colors_conditions)

    update_columns = ['CustomName']

    # Update the columns in the df_pno_colors_relation DataFrame
    for col in update_columns:
        df_pno_colors_relations[col] = data[col]
    all_columns = df_pno_colors_relations.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_pno_colors_relations, DBOperations.instance.config.get('RELATIONS', 'COL_Custom'), all_columns, conditional_columns)
    return 'Colors written successfully', 200

@bp_db_writer.route('/upholstery', methods=['POST'])
def write_upholstery(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
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

    df_pno_upholstery = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'UPH'), ['ID'], conditions=conditions)
    rel_ids = df_pno_upholstery['ID'].unique().tolist()
    uph_conditions = []
    if len(rel_ids) == 1:
        uph_conditions.append(f"RelationID = '{rel_ids[0]}'")
    else:
        uph_conditions.append(f"RelationID in {tuple(rel_ids)}")

    df_pno_upholstery_relations = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'UPH_Custom'), conditions=uph_conditions)

    update_columns = ['CustomName', 'CustomCategory']

    # Update the columns in the df_pno_upholstery_relation DataFrame
    for col in update_columns:
        df_pno_upholstery_relations[col] = data[col]
    all_columns = df_pno_upholstery_relations.columns.tolist()
    conditional_columns = list(set(all_columns) - set(update_columns))

    DBOperations.instance.upsert_data_from_df(df_pno_upholstery_relations, DBOperations.instance.config.get('RELATIONS', 'UPH_Custom'), all_columns, conditional_columns)
    return 'Upholstery written successfully', 200

@bp_db_writer.route('/packages', methods=['POST'])
def write_packages(country, model_year):
    data = request.get_json()
    if not data:
        return 'No data provided', 400
    
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
    return 'Packages written successfully', 200

@bp_db_writer.route('/sales-channels', methods=['POST'])
def upsert_sales_channel(country, model_year):
    data = request.json
    if not data:
        return 'No data provided', 400
    if 'ID' not in data:
        data['ID'] = str(uuid.uuid4())
    if 'StartDate' in data:
        data['StartDate'] = int(data['StartDate'])
    if 'EndDate' in data:
        data['EndDate'] = int(data['EndDate'])

    try:
        data['CountryCode'] = country
        # Create a DataFrame with a single row
        df_new_entry = pd.DataFrame([data])

        # Extract columns for upsert
        all_columns = df_new_entry.columns.tolist()
        conditional_columns = ['ID']

        # Perform the upsert
        DBOperations.instance.upsert_data_from_df(df_new_entry, DBOperations.instance.config.get('TABLES', 'SC'), all_columns, conditional_columns)
    except Exception as e:
        return str(e), 500
    
    return 'Sales channel created successfully', 200

@bp_db_writer.route('/sales-channels', methods=['DELETE'])
def delete_sales_channel(country, model_year):
    channel_id = request.args.get('ID')
    if not channel_id:
        return {"error": "Channel ID is required"}, 400
    
    discounts_df = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'DIS'), conditions=[f'ChannelID = {channel_id}'])
    if not discounts_df.empty:
        dis_ids = discounts_df['ID'].unique().tolist()
        for dis_id in dis_ids:
            delete_discount(dis_id)

    clo_df = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'CLO'), conditions=[f'ChannelID = {channel_id}'])
    if not clo_df.empty:
        clo_ids = clo_df['ID'].unique().tolist()
        for clo_id in clo_ids:
            delete_custom_local_options(clo_id)

    table_name = DBOperations.instance.config.get('TABLES', 'SC')
    delete_query = f"DELETE FROM {table_name} WHERE ID = ?"

    try:
        with DBOperations.instance.get_cursor() as cursor:
            cursor.execute(delete_query, (channel_id,))
        return {"message": "Record deleted successfully"}, 200
    except Exception as e:
        DBOperations.instance.logger.error(f"Error deleting record: {e}")
        return {"error": str(e)}, 500

@bp_db_writer.route('/discounts', methods=['POST'])
def upsert_discount(country, model_year):
    data = request.json
    if not data:
        return 'No data provided', 400
    if 'ID' not in data:
        data['ID'] = str(uuid.uuid4())
    if data.get('PNOSpecific', False) == 'true':
        data['PNOSpecific'] = 1
    else:
        data['PNOSpecific'] = 0

    try:
        if data['DiscountPercentage'] == '':
            data['DiscountPercentage'] = None
        if data['RetailPrice'] == '':
            data['RetailPrice'] = None
        if data['WholesalePrice'] == '':
            data['WholesalePrice'] = None
            
        if data['DiscountPercentage'] is not None:
            data['DiscountPercentage'] = float(data['DiscountPercentage'])
        if data['RetailPrice'] is not None:
            data['RetailPrice'] = float(data['RetailPrice'])
        if data['WholesalePrice'] is not None:
            data['WholesalePrice'] = float(data['WholesalePrice'])
        
        # Create a DataFrame with a single row
        df_new_entry = pd.DataFrame([data])

        # Extract columns for upsert
        all_columns = df_new_entry.columns.tolist()
        conditional_columns = ['ID']

        # Perform the upsert
        DBOperations.instance.upsert_data_from_df(df_new_entry, DBOperations.instance.config.get('TABLES', 'DIS'), all_columns, conditional_columns)
    except Exception as e:
        return str(e), 500
    
    return 'Discount created successfully', 200

@bp_db_writer.route('/discounts', methods=['DELETE'])
def delete_discount(country, model_year):
    discount_id = request.args.get('ID')
    if not discount_id:
        return {"error": "Discount ID is required"}, 400

    try:
        delete_discount(discount_id)
        return {"message": "Record deleted successfully"}, 200
    except Exception as e:
        DBOperations.instance.logger.error(f"Error deleting record: {e}")
        return {"error": str(e)}, 500

@bp_db_writer.route('/custom-local-options', methods=['POST'])
def upsert_custom_local_option(country, model_year):
    data = request.json
    if not data:
        return 'No data provided', 400
    if 'ID' not in data:
        data['ID'] = str(uuid.uuid4())
    try:
        data['FeatureRetailPrice'] = float(data['FeatureRetailPrice']) if data.get('FeatureRetailPrice') and data['FeatureRetailPrice'] != '' else 0
        data['FeatureWholesalePrice'] = float(data['FeatureWholesalePrice']) if data.get('FeatureWholesalePrice') and data['FeatureWholesalePrice'] != '' else 0

        # Create a DataFrame with a single row
        df_new_entry = pd.DataFrame([data])

        # Extract columns for upsert
        all_columns = df_new_entry.columns.tolist()
        conditional_columns = ['ID']

        # Perform the upsert
        DBOperations.instance.upsert_data_from_df(df_new_entry, DBOperations.instance.config.get('TABLES', 'CLO'), all_columns, conditional_columns)
    except Exception as e:
        return str(e), 500
    
    return 'Custom local option created successfully', 200

@bp_db_writer.route('/custom-local-options', methods=['DELETE'])
def remove_custom_local_option(country, model_year):
    id = request.args.get('ID')
    if not id:
        return {"error": "ID is required"}, 400
    try:
        delete_custom_local_options(id)
        return {"message": "Record deleted successfully"}, 200
    except Exception as e:
        DBOperations.instance.logger.error(f"Error deleting record: {e}")
        return {"error": str(e)}, 500
    
def delete_discount(id):
    table_name = DBOperations.instance.config.get('TABLES', 'DIS')
    delete_query = f"DELETE FROM {table_name} WHERE ID = ?"
    with DBOperations.instance.get_cursor() as cursor:
        cursor.execute(delete_query, (id,))

def delete_custom_local_options(id):
    table_name = DBOperations.instance.config.get('TABLES', 'CLO')
    delete_query = f"DELETE FROM {table_name} WHERE ID = ?"
    with DBOperations.instance.get_cursor() as cursor:
        cursor.execute(delete_query, (id,))

