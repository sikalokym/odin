import pandas as pd
from flask import Blueprint, request, jsonify

from src.database.db_operations import DBOperations
from src.database.services import get_engine_cats
from src.ingest.cpam.services import get_supported_countries
from src.ingest.visa_files.services import get_available_visa_files
from src.utils.db_utils import filter_df_by_model_year, filter_model_year_by_translation
from datetime import datetime, timedelta


bp_db_reader = Blueprint('db_reader', __name__, url_prefix='/api/db/<country>/<model_year>')

# if country is not in the url, return an error message before calling the function
@bp_db_reader.before_request
def check_country():
    country = request.view_args.get('country')
    if not country or country == 'undefined':
        return jsonify({"error": "Country code is missing or invalid"}), 400
    supported_countries = get_supported_countries(country)
    if supported_countries.empty:
        return jsonify({"error": "Country code is invalid"}), 400

@bp_db_reader.route('/engine_cats', methods=['GET'])
def retrieve_engine_cats(country, model_year):
    model = request.args.get('model')
    engine_cats = get_engine_cats(country, model_year, model)
    
    return jsonify(engine_cats)

@bp_db_reader.route('/pnos', methods=['GET'])
def get_pnos(country, model_year):
    columns = request.args.get('columns')
    if columns:
        columns = columns.split(',')
    else:
        columns = ['ID', 'Model', 'Engine', 'SalesVersion', 'Gearbox', 'StartDate', 'EndDate']

    if model_year == '0':
        return jsonify([])

    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), columns, conditions=[f"CountryCode = '{country}'"])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    
    ids = df_pnos['Model'].tolist()
    conditions = [f"CountryCode = '{country}'"]
    if len(ids) == 1:
        conditions.append(f"Code = '{ids[0]}'")
    else:
        conditions.append(f"Code in {tuple(ids)}")
    
    df_models = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'Typ'), columns=['Code', 'CustomName', 'StartDate', 'EndDate'], conditions=conditions)
    df_models = filter_df_by_model_year(df_models, model_year)
    df_models = filter_model_year_by_translation(df_models, conditional_columns=['CustomName'])
    df_models = df_models.drop(columns=['StartDate', 'EndDate'], axis=1)
    
    df_pnos = df_pnos.merge(df_models, how='left', left_on='Model', right_on='Code')
    df_pnos.drop(columns=['Code'], axis=1, inplace=True)
    df_pnos.drop_duplicates(inplace=True)
    return df_pnos.to_json(orient='records'), 200

@bp_db_reader.route('/models', methods=['GET'])
def get_models(country, model_year):
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['Model', 'StartDate', 'EndDate'], conditions=[f"CountryCode = '{country}'"])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    models = df_pnos['Model'].unique().tolist()
    conditions = [f"CountryCode = '{country}'"]
    if not models:
        return jsonify([])
    if len(models) == 1:
        conditions.append(f"Code = '{models[0]}'")
    else:
        conditions.append(f"Code in {tuple(models)}")

    df_models = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'Typ'), columns=['Code', 'CustomName', 'MarketText', 'StartDate', 'EndDate'], conditions=conditions)
    df_models = filter_df_by_model_year(df_models, model_year)
    df_models = filter_model_year_by_translation(df_models, conditional_columns=['CustomName'])
    df_models = df_models.drop(columns=['StartDate', 'EndDate'], axis=1)
    df_models.drop_duplicates(inplace=True)

    df_models = df_models.sort_values(by='Code', ascending=True)

    return df_models.to_json(orient='records')

@bp_db_reader.route('/sales_versions', methods=['GET'])
def get_sales_versions(country, model_year):
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['SalesVersion', 'StartDate', 'EndDate'], conditions=[f"CountryCode = '{country}'"])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    sales_versions = df_pnos['SalesVersion'].unique().tolist()
    conditions = [f"CountryCode = '{country}'"]
    if not sales_versions:
        return jsonify([])
    if len(sales_versions) == 1:
        conditions.append(f"Code = '{sales_versions[0]}'")
    else:
        conditions.append(f"Code in {tuple(sales_versions)}")
    
    df_sales_versions = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'SV'), columns=['Code', 'CustomName', 'MarketText', 'StartDate', 'EndDate'], conditions=conditions)
    df_sales_versions = filter_df_by_model_year(df_sales_versions, model_year)
    df_sales_versions = filter_model_year_by_translation(df_sales_versions, conditional_columns=['CustomName'])
    df_sales_versions = df_sales_versions.drop(columns=['StartDate', 'EndDate'], axis=1)
    df_sales_versions.drop_duplicates(inplace=True)

    df_sales_versions = df_sales_versions.sort_values(by='Code', ascending=True)

    return df_sales_versions.to_json(orient='records')

@bp_db_reader.route('/engines', methods=['GET'])
def get_engines(country, model_year):
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['Engine', 'StartDate', 'EndDate'], conditions=[f"CountryCode = '{country}'"])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    engine_codes = df_pnos['Engine'].unique().tolist()
    conditions = [f"CountryCode = '{country}'"]
    if not engine_codes:
        return jsonify([])
    elif len(engine_codes) == 1:
        conditions.append(f"Code = '{engine_codes[0]}'")
    else:
        conditions.append(f"Code in {tuple(engine_codes)}")
    
    df_engines = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'En'), columns=['Code', 'MarketText', 'CustomName', 'Performance', 'EngineCategory', 'EngineType', 'StartDate', 'EndDate'], conditions=conditions)
    df_engines = filter_df_by_model_year(df_engines, model_year)
    df_engines = filter_model_year_by_translation(df_engines, conditional_columns=['CustomName', 'Performance', 'EngineCategory', 'EngineType'])
    df_engines = df_engines.drop(columns=['StartDate', 'EndDate'], axis=1)
    df_engines.drop_duplicates(inplace=True)

    df_engines = df_engines.sort_values(by='Code', ascending=True)

    return df_engines.to_json(orient='records') 

@bp_db_reader.route('/gearboxes', methods=['GET'])
def get_gearboxes(country, model_year):
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['Gearbox', 'StartDate', 'EndDate'], conditions=[f"CountryCode = '{country}'"])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    gearbox_codes = df_pnos['Gearbox'].unique().tolist()
    conditions = [f"CountryCode = '{country}'"]
    if not gearbox_codes:
        return jsonify([])
    if len(gearbox_codes) == 1:
        conditions.append(f"Code = '{gearbox_codes[0]}'")
    else:
        conditions.append(f"Code in {tuple(gearbox_codes)}")
    
    df_gearboxes = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'G'), columns=['Code', 'CustomName', 'MarketText', 'StartDate', 'EndDate'], conditions=conditions)
    df_gearboxes = filter_df_by_model_year(df_gearboxes, model_year)
    df_gearboxes = filter_model_year_by_translation(df_gearboxes, conditional_columns=['CustomName'])
    df_gearboxes = df_gearboxes.drop(columns=['StartDate', 'EndDate'], axis=1)
    df_gearboxes.drop_duplicates(inplace=True)

    df_gearboxes = df_gearboxes.sort_values(by='Code', ascending=True)

    return df_gearboxes.to_json(orient='records')

@bp_db_reader.route('/options', methods=['GET'])
def get_options(country, model_year):
    model = request.args.get('model')
    engine = request.args.get('engine')
    sales_version = request.args.get('sales_version')
    gearbox = request.args.get('gearbox')

    conditions = [f"CountryCode = '{country}'"]
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'Model', 'StartDate', 'EndDate'], conditions=conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'OPT'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f"CountryCode = '{country}'"])
    df_options = filter_df_by_model_year(df_options, model_year)
    df_options.drop(columns=['StartDate', 'EndDate'], inplace=True)
    df_options.drop_duplicates(subset='Code', inplace=True)

    df_pno_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'OPT'), columns=['ID', 'PNOID', 'Code'], conditions=conditions)
    df_pno_options.drop_duplicates(inplace=True)
    
    df_options_custom = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'OPT_Custom'), columns=['RelationID', 'CustomName'])
    if df_options_custom.empty:
        df_pno_options['CustomName'] = ''
    else:
        df_pno_options = df_pno_options.merge(df_options_custom, how='inner', left_on='ID', right_on='RelationID')
        df_pno_options = df_pno_options.drop(columns=['RelationID'])
    
    df_pno_options['MarketText'] = df_pno_options['Code'].map(df_options.set_index('Code')['MarketText'])
    df_pno_options.drop(columns=['ID'], inplace=True)

    df_pno_features = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'FEAT'), columns=['PNOID', 'Code as FeatCode', 'Reference', 'CustomName as FeatText', 'CustomCategory'], conditions=conditions)

    # remove (u) from the end of the reference if exists otherwise replace with drop
    df_pno_options['OptCode'] = df_pno_options['Code'].apply(lambda x: x.lstrip('0') if x.isnumeric() else x)
    
    df_pno_options_merged = df_pno_options.merge(df_pno_features[['PNOID', 'FeatCode', 'FeatText', 'CustomCategory', 'Reference']], 
                                      how='left', 
                                      left_on=['PNOID', 'OptCode'], 
                                      right_on=['PNOID', 'Reference'])

    df_pno_options_merged['Code'] = df_pno_options_merged.apply(lambda row: row['Code'] + " (" + row['FeatCode'].strip() + ")" if pd.notnull(row['FeatCode']) else row['Code'], axis=1)
    df_pno_options_merged['hasFeature'] = df_pno_options_merged['Reference'].apply(lambda x: False if pd.isnull(x) or x == '' else True)
    df_pno_options_merged['CustomName'] = df_pno_options_merged['FeatText'].combine_first(df_pno_options_merged['CustomName'])

    # Create mappings
    pno_id_to_model = df_pnos.set_index('ID')['Model'].to_dict()
    custom_name_to_pnoid = df_pno_options_merged.groupby('CustomName')['PNOID'].apply(list).to_dict()

    # Aggregate data
    def aggregate_custom_name(custom_names):
        filtered_df = custom_names[custom_names.notnull() & (custom_names != "") & (custom_names != "Null")]
        
        # Strip and remove duplicates
        unique_names = filtered_df.unique()
        
        if len(unique_names) == 0:
            return ''
        elif len(unique_names) > 1:
            res_str = ''
            for name in unique_names:
                models = set()
                if name:
                    pno_ids = custom_name_to_pnoid.get(name, [])
                    for pno_id in pno_ids:
                        model = pno_id_to_model.get(pno_id, '')
                        if model:
                            models.add(model)
                if models:
                    res_str += f"({', '.join(sorted(models))}), "
                    
            return "Specific: " + res_str[:-2]
        return unique_names[0]
    
    df_pno_options_merged = df_pno_options_merged.groupby('Code').agg({
        'MarketText': 'first', 
        'CustomName': aggregate_custom_name,
        'CustomCategory': 'first',
        'hasFeature': 'first'
    }).reset_index()
    
    df_final = df_pno_options_merged.sort_values(by='Code', ascending=True)
    df_final = df_final[['Code', 'MarketText', 'CustomName', 'CustomCategory', 'hasFeature']]
    df_final.drop_duplicates(inplace=True)

    return df_final.to_json(orient='records')

@bp_db_reader.route('/colors', methods=['GET'])
def get_colors(country, model_year):
    model = request.args.get('model')
    engine = request.args.get('engine')
    sales_version = request.args.get('sales_version')
    gearbox = request.args.get('gearbox')

    conditions = [f"CountryCode = '{country}'"]
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")

    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'Model', 'StartDate', 'EndDate'], conditions=conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_colors = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'COL'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f"CountryCode = '{country}'"])
    df_colors = filter_df_by_model_year(df_colors, model_year)
    df_colors.drop(columns=['StartDate', 'EndDate'], inplace=True)
    df_colors.drop_duplicates(subset='Code', inplace=True)

    df_pno_colors = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'COL'), columns=['ID', 'PNOID', 'Code'], conditions=conditions)
    df_pno_colors.drop_duplicates(inplace=True)
    
    df_colors_custom = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'COL_Custom'), columns=['RelationID', 'CustomName'])
    if df_colors_custom.empty:
        df_pno_colors['CustomName'] = ''
    else:
        df_pno_colors = df_pno_colors.merge(df_colors_custom, how='inner', left_on='ID', right_on='RelationID')
        df_pno_colors = df_pno_colors.drop(columns=['RelationID'])
    
    df_pno_colors['MarketText'] = df_pno_colors['Code'].map(df_colors.set_index('Code')['MarketText'])
    df_pno_colors.drop(columns=['ID'], inplace=True)
    
    # Create mappings
    pno_id_to_model = df_pnos.set_index('ID')['Model'].to_dict()
    custom_name_to_pnoid = df_pno_colors.groupby('CustomName')['PNOID'].apply(list).to_dict()

    # Aggregate data
    def aggregate_custom_name(custom_names):
        filtered_df = custom_names[custom_names.notnull() & (custom_names != "") & (custom_names != "Null")]
        
        # Strip and remove duplicates
        unique_names = filtered_df.unique()
        
        if len(unique_names) == 0:
            return ''
        elif len(unique_names) > 1:
            res_str = ''
            for name in unique_names:
                models = set()
                if name:
                    pno_ids = custom_name_to_pnoid.get(name, [])
                    for pno_id in pno_ids:
                        model = pno_id_to_model.get(pno_id, '')
                        if model:
                            models.add(model)
                if models:
                    res_str += f"({', '.join(sorted(models))}), "
                    
            return "Specific: " + res_str[:-2]
        return unique_names[0]
    
    df_pno_colors = df_pno_colors.groupby('Code').agg({
        'MarketText': 'first', 
        'CustomName': aggregate_custom_name
    }).reset_index()
    
    df_pno_colors = df_pno_colors.sort_values(by='Code', ascending=True)
    df_pno_colors.drop_duplicates(inplace=True)
    
    return df_pno_colors.to_json(orient='records')

@bp_db_reader.route('/upholstery', methods=['GET'])
def get_upholstery(country, model_year):
    model = request.args.get('model')
    engine = request.args.get('engine')
    sales_version = request.args.get('sales_version')
    gearbox = request.args.get('gearbox')

    conditions = [f"CountryCode = '{country}'"]
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'Model', 'StartDate', 'EndDate'], conditions=conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_upholstery = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'UPH'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f"CountryCode = '{country}'"])
    df_upholstery = filter_df_by_model_year(df_upholstery, model_year)
    df_upholstery.drop(columns=['StartDate', 'EndDate'], inplace=True)
    df_upholstery.drop_duplicates(subset='Code', inplace=True)

    df_pno_upholstery = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'UPH'), columns=['ID', 'PNOID', 'Code'], conditions=conditions)
    df_pno_upholstery.drop_duplicates(inplace=True)
    
    df_upholstery_custom = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'UPH_Custom'), columns=['RelationID', 'CustomName', 'CustomCategory'])
    if df_upholstery_custom.empty:
        df_pno_upholstery['CustomName'] = ''
        df_pno_upholstery['CustomCategory'] = ''
    else:
        df_pno_upholstery = df_pno_upholstery.merge(df_upholstery_custom, how='inner', left_on='ID', right_on='RelationID')
        df_pno_upholstery = df_pno_upholstery.drop(columns=['RelationID'])
    
    df_pno_upholstery['MarketText'] = df_pno_upholstery['Code'].map(df_upholstery.set_index('Code')['MarketText'])
    df_pno_upholstery.drop_duplicates(inplace=True)

    # Create mappings
    pno_id_to_model = df_pnos.set_index('ID')['Model'].to_dict()
    custom_name_to_pnoid = df_pno_upholstery.groupby('CustomName')['PNOID'].apply(list).to_dict()
    df_pno_upholstery.drop(columns=['ID', 'PNOID'], inplace=True)

    # Aggregate data
    def aggregate_custom_name(custom_names):
        filtered_df = custom_names[custom_names.notnull() & (custom_names != "") & (custom_names != "Null")]
        
        # Strip and remove duplicates
        unique_names = filtered_df.unique()
        
        if len(unique_names) == 0:
            return ''
        elif len(unique_names) > 1:
            res_str = ''
            for name in unique_names:
                models = set()
                if name:
                    pno_ids = custom_name_to_pnoid.get(name, [])
                    for pno_id in pno_ids:
                        model = pno_id_to_model.get(pno_id, '')
                        if model:
                            models.add(model)
                if models:
                    res_str += f"({', '.join(sorted(models))}), "
                    
            return "Specific: " + res_str[:-2]
        return unique_names[0]
    
    df_pno_upholstery = df_pno_upholstery.groupby('Code').agg({
        'MarketText': 'first', 
        'CustomName': aggregate_custom_name,
        'CustomCategory': 'first'
    }).reset_index()
    
    df_pno_upholstery = df_pno_upholstery.sort_values(by='Code', ascending=True)
    
    return df_pno_upholstery.to_json(orient='records')

@bp_db_reader.route('/features', methods=['GET'])
def get_features(country, model_year):
    model = request.args.get('model')
    engine = request.args.get('engine')
    sales_version = request.args.get('sales_version')
    gearbox = request.args.get('gearbox')

    # Prepare initial conditions for the PNO query
    conditions = [f"CountryCode = '{country}'"]
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")

    # Query PNO data and filter by model year
    df_pnos = DBOperations.instance.get_table_df(
        DBOperations.instance.config.get('AUTH', 'PNO'),
        ['ID', 'Model', 'StartDate', 'EndDate'],
        conditions=conditions
    )
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])

    # Prepare conditions for the FEAT and CFEAT queries
    ids = df_pnos['ID'].tolist()
    pno_conditions = [f"PNOID = '{ids[0]}'"] if len(ids) == 1 else [f"PNOID in {tuple(ids)}"]

    # Query features and filter by model year
    df_features = DBOperations.instance.get_table_df(
        DBOperations.instance.config.get('TABLES', 'FEA'),
        columns=['Code', 'MarketText', 'StartDate', 'EndDate'],
        conditions=[f"CountryCode = '{country}'"]
    )
    df_features = filter_df_by_model_year(df_features, model_year)
    df_features.drop(columns=['StartDate', 'EndDate'], inplace=True)
    df_features['Code'] = df_features['Code'].str.strip()
    df_features.drop_duplicates(subset='Code', inplace=True)

    # Query PNO features and custom features
    df_pno_features = DBOperations.instance.get_table_df(
        DBOperations.instance.config.get('AUTH', 'FEAT'),
        columns=['PNOID', 'Code', 'CustomName', 'CustomCategory'],
        conditions=pno_conditions
    )
    df_pno_custom_features = DBOperations.instance.get_table_df(
        DBOperations.instance.config.get('AUTH', 'CFEAT'),
        columns=['PNOID', 'ID', 'Code', 'CustomName', 'CustomCategory'],
        conditions=pno_conditions
    )

    # Combine features and custom features
    df_pno_features = pd.concat([df_pno_features, df_pno_custom_features], ignore_index=True)
    df_pno_features['Code'] = df_pno_features['Code'].str.strip()
    df_pno_features['MarketText'] = df_pno_features['Code'].map(df_features.set_index('Code')['MarketText'])
    df_pno_features['ID'] = df_pno_features['ID'].fillna('')

    # Create mappings
    pno_id_to_model = df_pnos.set_index('ID')['Model'].to_dict()
    custom_name_to_pnoid = df_pno_features.groupby('CustomName')['PNOID'].apply(list).to_dict()

    # Aggregate data
    def aggregate_custom_name(custom_names):
        filtered_df = custom_names[custom_names.notnull() & (custom_names != "") & (custom_names != "Null")]
        
        # Strip and remove duplicates
        unique_names = filtered_df.unique()
        
        if len(unique_names) == 0:
            return ''
        elif len(unique_names) > 1:
            res_str = ''
            for name in unique_names:
                
                models = set()
                if name:
                    pno_ids = custom_name_to_pnoid.get(name, [])
                    for pno_id in pno_ids:
                        model = pno_id_to_model.get(pno_id, '')
                        if model:
                            models.add(model)
                if models:
                    res_str += f"({', '.join(sorted(models))}), "
                    
            return "Specific: " + res_str[:-2]
        return unique_names[0]
    
    df_pno_features = df_pno_features.groupby('Code').agg({
        'MarketText': 'first', 
        'CustomName': aggregate_custom_name,
        'CustomCategory': 'first', 
        'ID': lambda x: ','.join(x) if x.any() else ''
    }).reset_index()

    # Sort and remove duplicates
    df_pno_features = df_pno_features.sort_values(by='Code', ascending=True)
    df_pno_features.drop_duplicates(inplace=True)

    # Return as JSON
    return df_pno_features.to_json(orient='records')

@bp_db_reader.route('/packages', methods=['GET'])
def get_packages(country, model_year):
    model = request.args.get('model')
    engine = request.args.get('engine')
    sales_version = request.args.get('sales_version')
    gearbox = request.args.get('gearbox')

    conditions = [f"CountryCode = '{country}'"]
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'Model', 'StartDate', 'EndDate'], conditions=conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])

    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_packages = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'PKG'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f"CountryCode = '{country}'"])
    df_packages = filter_df_by_model_year(df_packages, model_year)
    df_packages.drop(columns=['StartDate', 'EndDate'], inplace=True)
    df_packages.drop_duplicates(subset='Code', inplace=True)
    
    df_pno_packages = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PKG'), columns=['ID', 'PNOID', 'Code'], conditions=conditions)
    df_pno_packages.drop_duplicates(inplace=True)

    df_packages_custom = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'PKG_Custom'), columns=['RelationID', 'CustomName'])
    if df_packages_custom.empty:
        df_pno_packages['CustomName'] = ''
    else:
        df_pno_packages = df_pno_packages.merge(df_packages_custom, how='inner', left_on='ID', right_on='RelationID')
        df_pno_packages = df_pno_packages.drop(columns=['RelationID'])
    
    df_pno_packages['MarketText'] = df_pno_packages['Code'].map(df_packages.set_index('Code')['MarketText'])
    df_pno_packages.drop_duplicates(inplace=True)

    # Create mappings
    pno_id_to_model = df_pnos.set_index('ID')['Model'].to_dict()
    custom_name_to_pnoid = df_pno_packages.groupby('CustomName')['PNOID'].apply(list).to_dict()

    # Aggregate data
    def aggregate_custom_name(custom_names):
        filtered_df = custom_names[custom_names.notnull() & (custom_names != "") & (custom_names != "Null")]
        
        # Strip and remove duplicates
        unique_names = filtered_df.unique()
        
        if len(unique_names) == 0:
            return ''
        elif len(unique_names) > 1:
            res_str = ''
            for name in unique_names:
                models = set()
                if name:
                    pno_ids = custom_name_to_pnoid.get(name, [])
                    for pno_id in pno_ids:
                        model = pno_id_to_model.get(pno_id, '')
                        if model:
                            models.add(model)
                if models:
                    res_str += f"({', '.join(sorted(models))}), "
                    
            return "Specific: " + res_str[:-2]
        return unique_names[0]
    
    df_pno_packages = df_pno_packages.groupby('Code').agg({
        'MarketText': 'first', 
        'CustomName': aggregate_custom_name
    }).reset_index()

    df_pno_packages = df_pno_packages.sort_values(by='Code', ascending=True)
    
    return df_pno_packages.to_json(orient='records')

import pandas as pd

@bp_db_reader.route('/changelog', methods=['GET'])
def get_changelog(country, model_year):
    conditions = [f"CountryCode = '{country}'"]

    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'Model', 'Engine', 'SalesVersion', 'Gearbox', 'StartDate', 'EndDate'], conditions=conditions)
    if df_pnos.empty:
        return jsonify([])
    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"CHANGECODE = '{ids[0]}'")
    else:
        conditions.append(f"CHANGECODE in {tuple(ids)}")

    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d %H:%M:%S.000')
    conditions.append(f"ChangeDate >= '{seven_days_ago_str}'")

    df_pno_changelog = DBOperations.instance.get_table_df(DBOperations.instance.config.get('DQ', 'CL'), columns=['ChangeTable', 'ChangeDate', 'ChangeType', 'ChangeField', 'ChangeFrom', 'ChangeTo', 'CHANGECODE'], conditions=conditions)
    df_pno_changelog = df_pno_changelog.sort_values(by='ChangeDate', ascending=False)
    df_pno_changelog = df_pno_changelog[df_pno_changelog['ChangeType'] != 'Insert']

    # Merge df_pno_changelog with df_pnos to add the Model, Engine, SalesVersion, and Gearbox columns
    df_pno_changelog = pd.merge(df_pno_changelog, df_pnos, left_on='CHANGECODE', right_on='ID', how='left')

    

    # After merging df_pno_changelog with df_pnos
    # Remove "PNO" except when part of "PNOCustom", remove "Custom" if not "PNOCustom", and replace "PNOOptionsCustom" with "Options"
    df_pno_changelog['ChangeTable'] = df_pno_changelog['ChangeTable'].apply(
        lambda x: x.replace('Custom', '') if 'PNOCustom' not in x else x
    )
    df_pno_changelog['ChangeTable'] = df_pno_changelog['ChangeTable'].apply(
        lambda x: x.replace('PNO', '') if 'PNOCustom' not in x else x
    )
    df_pno_changelog['ChangeTable'] = df_pno_changelog['ChangeTable'].apply(
        lambda x: x.replace('Custom', '') if 'PNOCustom' in x else x
    )

    # Select the columns to keep in the final DataFrame
    final_columns = ['ChangeTable', 'ChangeDate', 'ChangeType', 'ChangeField', 'ChangeFrom', 'ChangeTo', 'Model', 'Engine', 'SalesVersion', 'Gearbox']
    df_pno_changelog = df_pno_changelog[final_columns]

    return df_pno_changelog.to_json(orient='records')

@bp_db_reader.route('/dq-log', methods=['GET'])
def get_dq_log(country, model_year):
    LogType = request.args.get('LogType', None)
    conditions = [f"CountryCode = '{country}' OR CountryCode = 'All'"]

    # Calculate the date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    # Format it to match the LogDate column format
    seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d %H:%M:%S.000')
    # Add condition to filter out LogDate values older than 7 days
    conditions.append(f"LogDate >= '{seven_days_ago_str}'")

    df_pno_dqlog = DBOperations.instance.get_table_df(DBOperations.instance.config.get('DQ', 'DQ'), columns=['LogDate', 'LogMessage', 'LogType'], conditions=conditions)
    df_pno_dqlog = df_pno_dqlog.sort_values(by='LogDate', ascending=False)

    # Drop rows where LogType is not equal to the provided LogType argument
    if LogType:
        df_pno_dqlog = df_pno_dqlog[df_pno_dqlog['LogType'] == LogType]

    return df_pno_dqlog.to_json(orient='records')

@bp_db_reader.route('/sales-channels', methods=['GET'])
def get_sales_channels(country, model_year):
    conditions = [f"CountryCode = '{country}'", f"ModelYear = '{model_year}'"]
    df_sales_channels = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'SC'), columns=['ID', 'Code', 'ChannelName', 'Comment', 'DateFrom', 'DateTo'], conditions=conditions)
    
    df_sales_channels = df_sales_channels.sort_values(by='Code', ascending=True)

    # Convert DateFrom and DateTo columns to datetime format
    df_sales_channels['DateFrom'] = pd.to_datetime(df_sales_channels['DateFrom'])
    df_sales_channels['DateTo'] = pd.to_datetime(df_sales_channels['DateTo'])
    
    # Filter where either start or end date are in the model year. don't use filter_df_by_model_year
    df_sales_channels = df_sales_channels[(df_sales_channels['DateFrom'].dt.year <= int(model_year)) & (df_sales_channels['DateTo'].dt.year >= int(model_year))]
    
    # Format DateFrom and DateTo columns
    df_sales_channels['DateFrom'] = df_sales_channels['DateFrom'].dt.strftime('%Y-%m-%d')
    df_sales_channels['DateTo'] = df_sales_channels['DateTo'].dt.strftime('%Y-%m-%d')
    return df_sales_channels.to_json(orient='records')

@bp_db_reader.route('/discounts', methods=['GET'])
def get_discounts(country, model_year):
    sales_channels_id = request.args.get('id')
    conditions = [f"ChannelID = '{sales_channels_id}'"]

    df_discounts = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'DIS'), columns=['ID', 'ChannelID', 'DiscountPercentage', 'RetailPrice', 'WholesalePrice', 'PNOSpecific', 'AffectedVisaFile'], conditions=conditions)
    
    # split AffectedVisaFile column by comma if not All else return a list with no elements
    df_discounts['AffectedVisaFile'] = df_discounts['AffectedVisaFile'].replace('All', None)
    df_discounts['AffectedVisaFile'] = df_discounts['AffectedVisaFile'].map(lambda x: x.split(',') if x else [])

    df_discounts = df_discounts.sort_values(by='DiscountPercentage', ascending=True)

    return df_discounts.to_json(orient='records')

@bp_db_reader.route('/custom-local-options', methods=['GET'])
def get_custom_local_options(country, model_year):
    channel_id = request.args.get('id')
    conditions = [f"ChannelID = '{channel_id}'"]

    df_custom_local_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'CLO'), columns=['ID', 'FeatureCode', 'FeatureRetailPrice', 'FeatureWholesalePrice', 'AffectedVisaFile', 'DateFrom', 'DateTo'], conditions=conditions)
    
    # Convert DateFrom and DateTo columns to datetime format
    df_custom_local_options['DateFrom'] = pd.to_datetime(df_custom_local_options['DateFrom'])
    df_custom_local_options['DateTo'] = pd.to_datetime(df_custom_local_options['DateTo'])
    
    # Format DateFrom and DateTo columns
    df_custom_local_options['DateFrom'] = df_custom_local_options['DateFrom'].dt.strftime('%Y-%m-%d')
    df_custom_local_options['DateTo'] = df_custom_local_options['DateTo'].dt.strftime('%Y-%m-%d')
    
    # split AffectedVisaFile column by comma if not All else return a list with no elements
    df_custom_local_options['AffectedVisaFile'] = df_custom_local_options['AffectedVisaFile'].replace('All', None)
    df_custom_local_options['AffectedVisaFile'] = df_custom_local_options['AffectedVisaFile'].map(lambda x: x.split(',') if x else [])
    df_custom_local_options = df_custom_local_options.sort_values(by='FeatureCode', ascending=True)

    return df_custom_local_options.to_json(orient='records')

@bp_db_reader.route('/visa-files', methods=['GET'])
def get_visa_files(country, model_year):
    try:
        # Load available Visa files
        visa_columns = ['VisaFile', 'CarType']
        df_visa = get_available_visa_files(country, model_year, visa_columns)
        if df_visa.empty:
            return jsonify([])
        
        df_visa.drop_duplicates(inplace=True)
            
        codes = df_visa['CarType'].tolist()
        conditions = [f"CountryCode = '{country}'"]
        if len(codes) == 1:
            conditions.append(f"Code = '{codes[0]}'")
        else:
            conditions.append(f"Code in {tuple(codes)}")
        
        df_models = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'Typ'), columns=['Code', 'CustomName', 'StartDate', 'EndDate'], conditions=conditions)
        df_models = filter_df_by_model_year(df_models, model_year)
        df_models = filter_model_year_by_translation(df_models, conditional_columns=['CustomName'])
        df_models = df_models.drop(columns=['StartDate', 'EndDate'], axis=1)
        
        df_visa = df_visa.merge(df_models, how='left', left_on='CarType', right_on='Code')
        df_visa.drop(columns=['Code'], axis=1, inplace=True)
        df_visa.drop_duplicates(inplace=True)
        return df_visa.to_json(orient='records'), 200
    except Exception as e:
        return str(e), 500

# get visa file data
@bp_db_reader.route('/visa-file', methods=['GET'])
def get_visa_file_data(country, model_year):
    visa_file = request.args.get('VisaFile')
    conditions = [f"VisaFile = '{visa_file}'", f"CountryCode = '{country}'", f"ModelYear = '{model_year}'"]

    df_visa_file = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), conditions=conditions)
    df_visa_file.drop(columns=['LoadingDate', 'CountryCode'], inplace=True)
    return df_visa_file.to_json(orient='records')
