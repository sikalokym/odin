import pandas as pd
from flask import Blueprint, request, jsonify

from src.database.db_operations import DBOperations
from src.database.services import get_engine_cats
from src.ingest.visa_files.services import get_available_visa_files
from src.utils.db_utils import filter_df_by_model_year, filter_model_year_by_translation, get_column_map


bp_db_reader = Blueprint('db_reader', __name__, url_prefix='/api/db/<country>/<model_year>')


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

    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), columns, conditions=[f'CountryCode = {country}'])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    
    df_pnos.drop_duplicates(inplace=True)
    return df_pnos.to_json(orient='records')

@bp_db_reader.route('/models', methods=['GET'])
def get_models(country, model_year):
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['Model', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    models = df_pnos['Model'].unique().tolist()
    conditions = [f'CountryCode = {country}']
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
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['SalesVersion', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    sales_versions = df_pnos['SalesVersion'].unique().tolist()
    conditions = [f'CountryCode = {country}']
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
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['Engine', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    engine_codes = df_pnos['Engine'].unique().tolist()
    conditions = [f'CountryCode = {country}']
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
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['Gearbox', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    gearbox_codes = df_pnos['Gearbox'].unique().tolist()
    conditions = [f'CountryCode = {country}']
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

    conditions = [f'CountryCode = {country}']
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'OPT'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
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

    # group by code. if the number of custom names is more than one, change the custom name to '*Model-specific text*'
    df_pno_options_merged = df_pno_options_merged.groupby('Code').agg({
        'MarketText': 'first', 
        'CustomName': lambda x: '*Model-specific text*' if len(x.unique()) > 1 else x.unique()[0],
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

    conditions = [f'CountryCode = {country}']
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")

    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_colors = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'COL'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
    df_colors = filter_df_by_model_year(df_colors, model_year)
    df_colors.drop(columns=['StartDate', 'EndDate'], inplace=True)
    df_colors.drop_duplicates(subset='Code', inplace=True)

    df_pno_colors = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'COL'), columns=['ID', 'Code'], conditions=conditions)
    df_pno_colors.drop_duplicates(inplace=True)
    
    df_colors_custom = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'COL_Custom'), columns=['RelationID', 'CustomName'])
    if df_colors_custom.empty:
        df_pno_colors['CustomName'] = ''
    else:
        df_pno_colors = df_pno_colors.merge(df_colors_custom, how='inner', left_on='ID', right_on='RelationID')
        df_pno_colors = df_pno_colors.drop(columns=['RelationID'])
    
    df_pno_colors['MarketText'] = df_pno_colors['Code'].map(df_colors.set_index('Code')['MarketText'])
    df_pno_colors.drop(columns=['ID'], inplace=True)
    
    # group by code. if the number of custom names is more than one, change the custom name to '*Model-specific text*'
    df_pno_colors = df_pno_colors.groupby('Code').agg({'MarketText': 'first', 'CustomName': lambda x: '*Model-specific text*' if len(x.unique()) > 1 else x.unique()[0]}).reset_index()

    df_pno_colors = df_pno_colors.sort_values(by='Code', ascending=True)
    df_pno_colors.drop_duplicates(inplace=True)
    
    return df_pno_colors.to_json(orient='records')

@bp_db_reader.route('/upholstery', methods=['GET'])
def get_upholstery(country, model_year):
    model = request.args.get('model')
    engine = request.args.get('engine')
    sales_version = request.args.get('sales_version')
    gearbox = request.args.get('gearbox')

    conditions = [f'CountryCode = {country}']
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_upholstery = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'UPH'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
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
    df_pno_upholstery.drop(columns=['ID', 'PNOID'], inplace=True)
    df_pno_upholstery.drop_duplicates(inplace=True)

    # group by code. if the number of custom names is more than one, change the custom name to '*Model-specific text*'
    df_pno_upholstery = df_pno_upholstery.groupby('Code').agg({'MarketText': 'first', 'CustomName': lambda x: '*Model-specific text*' if len(x.unique()) > 1 else x.unique()[0], 'CustomCategory': 'first'}).reset_index()

    df_pno_upholstery = df_pno_upholstery.sort_values(by='Code', ascending=True)
    
    return df_pno_upholstery.to_json(orient='records')

@bp_db_reader.route('/features', methods=['GET'])
def get_features(country, model_year):
    model = request.args.get('model')
    engine = request.args.get('engine')
    sales_version = request.args.get('sales_version')
    gearbox = request.args.get('gearbox')

    conditions = [f'CountryCode = {country}']
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

    df_features = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'FEA'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
    df_features = filter_df_by_model_year(df_features, model_year)
    df_features.drop(columns=['StartDate', 'EndDate'], inplace=True)
    df_features['Code'] = df_features['Code'].str.strip()
    df_features.drop_duplicates(subset='Code', inplace=True)

    df_pno_features = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'FEAT'), columns=['PNOID', 'Code', 'CustomName', 'CustomCategory'], conditions=conditions)
    df_pno_features['Code'] = df_pno_features['Code'].str.strip()
    df_pno_features['MarketText'] = df_pno_features['Code'].map(df_features.set_index('Code')['MarketText'])
    df_pno_features['ID'] = ''

    df_pno_custom_features = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'CFEAT'), columns=['PNOID', 'ID', 'Code', 'CustomName', 'CustomCategory'], conditions=conditions)

    df_pno_features = pd.concat([df_pno_features, df_pno_custom_features], ignore_index=True)

    # Create a mapping from PNOID to Model
    pno_id_to_model = df_pnos.set_index('ID')['Model'].to_dict()
    
    # Create a mapping from CustomName to PNOID in df_pno_features
    custom_name_to_pnoid = df_pno_features.set_index('CustomName')['PNOID'].to_dict()
    
    # Use the mappings in the aggregation
    df_pno_features = df_pno_features.groupby('Code').agg({
        'MarketText': 'first', 
        'CustomName': lambda x: "Specific: " + ', '.join(sorted([model for model in (pno_id_to_model.get(custom_name_to_pnoid.get(i, 'Unknown'), 'Unknown') for i in x.replace([None, "", "Null"], "Common").unique()) if model != 'Unknown'])) if len(x.replace([None, "", "Null"], "Common").unique()) > 1 else x.unique()[0],
        'CustomCategory': 'first', 
        'ID': lambda x: ','.join(x) if x.any() else ''
    }).reset_index()
    
    df_pno_features = df_pno_features.sort_values(by='Code', ascending=True)
    df_pno_features.drop_duplicates(inplace=True)

    return df_pno_features.to_json(orient='records')

@bp_db_reader.route('/packages', methods=['GET'])
def get_packages(country, model_year):
    model = request.args.get('model')
    engine = request.args.get('engine')
    sales_version = request.args.get('sales_version')
    gearbox = request.args.get('gearbox')

    conditions = [f'CountryCode = {country}']
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")
    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"PNOID = '{ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(ids)}")

    df_packages = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'PKG'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
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
    df_pno_packages.drop(columns=['ID', 'PNOID'], inplace=True)
    df_pno_packages.drop_duplicates(inplace=True)

    # group by code. if the number of custom names is more than one, change the custom name to '*Model-specific text*'
    df_pno_packages = df_pno_packages.groupby('Code').agg({'MarketText': 'first', 'CustomName': lambda x: '*Model-specific text*' if len(x.unique()) > 1 else x.unique()[0]}).reset_index()

    df_pno_packages = df_pno_packages.sort_values(by='Code', ascending=True)
    
    return df_pno_packages.to_json(orient='records')

@bp_db_reader.route('/changelog', methods=['GET'])
def get_changelog(country, model_year):
    model = request.args.get('model')

    conditions = [f'CountryCode = {country}']
    if model:
        conditions.append(f"Model = '{model}'")

    df_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), ['ID', 'StartDate', 'EndDate'], conditions=conditions)
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return jsonify([])
    ids = df_pnos['ID'].tolist()
    conditions = []
    if len(ids) == 1:
        conditions.append(f"CHANGECODE = '{ids[0]}'")
    else:
        conditions.append(f"CHANGECODE in {tuple(ids)}")

    df_pno_features = DBOperations.instance.get_table_df(DBOperations.instance.config.get('DQ', 'CL'), columns=['ChangeTable', 'ChangeDate', 'ChangeType', 'ChangeField', 'ChangeFrom', 'ChangeTo'], conditions=conditions)
    df_pno_features = df_pno_features.sort_values(by='ChangeDate', ascending=True)

    return df_pno_features.to_json(orient='records')

@bp_db_reader.route('/sales-channels', methods=['GET'])
def get_sales_channels(country, model_year):
    df_sales_channels = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'SC'), columns=['ID', 'Code', 'ChannelName', 'Comment', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
    df_sales_channels = filter_df_by_model_year(df_sales_channels, model_year)
    
    df_sales_channels = df_sales_channels.sort_values(by='Code', ascending=True)

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

    df_custom_local_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'CLO'), columns=['ID', 'FeatureCode', 'FeatureRetailPrice', 'FeatureWholesalePrice', 'AffectedVisaFile', 'StartDate', 'EndDate'], conditions=conditions)
    
    # split AffectedVisaFile column by comma if not All else return a list with no elements
    df_custom_local_options['AffectedVisaFile'] = df_custom_local_options['AffectedVisaFile'].replace('All', None)
    df_custom_local_options['AffectedVisaFile'] = df_custom_local_options['AffectedVisaFile'].map(lambda x: x.split(',') if x else [])
    df_custom_local_options = df_custom_local_options.sort_values(by='FeatureCode', ascending=True)

    return df_custom_local_options.to_json(orient='records')

@bp_db_reader.route('/visa-files', methods=['GET'])
def get_visa_files(country, model_year):
    try:
        # Load available Visa files
        df_visa = get_available_visa_files(country, model_year)
        
        df_visa.drop_duplicates(inplace=True)
        
        records = df_visa.to_dict(orient='records')
        return jsonify(records), 200
    except Exception as e:
        return str(e), 500
