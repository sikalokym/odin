from io import BytesIO
from openpyxl import Workbook
from src.database.db_operations import DBOperations
from src.export.variant_binder import prices_sheet, options_sheet, upholstery_colors_sheet
from src.utils.db_utils import filter_df_by_timestamp


def extract_variant_binder(country, model, engines_types, time):
    wb = Workbook()

    # Remove the default sheet created
    default_sheet = wb.active
    wb.remove(default_sheet)

    valid_engines = get_valid_engines(country, engines_types, time)
    valid_pnos = get_valid_pnos(country, model, time, valid_engines)
    sales_versions = get_sales_versions(country, valid_pnos, time)
    title = get_model_name(model, time)

    if valid_pnos.empty or sales_versions.empty or valid_engines.empty:
        DBOperations.instance.logger.info(f"No data found for model {model} and engine category {engines_types} at time {time}")
        return None
    ws_1 = wb.create_sheet("Preise")
    prices_sheet.get_sheet(ws_1, valid_pnos, sales_versions, title, time, valid_engines, country)
    ws_2 = wb.create_sheet("Optionen")
    options_sheet.get_sheet(ws_2, sales_versions, title, country)
    ws_3 = wb.create_sheet("Polster & Farben")
    upholstery_colors_sheet.get_sheet(ws_3, sales_versions, title, country)

    wb.save(f'dist/VB {title} {engines_types} {time}.xlsx')
    return
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output
    
def get_model_name(country, model, time):
    models = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'Typ'), conditions=[f'CountryCode = {country}'])

    # filter models where StartDate and End Data wrap the current time for the given model
    df_model = filter_df_by_timestamp(models, time)
    df_model = models[models['Code'] == model]

    # return the model name
    return df_model['MarketText'].values[0]

def get_sales_versions(country, pnos, time):
    df_sv = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'SV'), conditions=[f'CountryCode = {country}'])
    df_pno_price = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'PNO_Custom'))
    df_sv = filter_df_by_timestamp(df_sv, time)
    df_sv.rename(columns={'Code': 'TmpCode'}, inplace=True)

    df_allowed_sv = pnos.merge(df_sv[['TmpCode', 'MarketText']], left_on='SalesVersion', right_on='TmpCode', how='left')
    df_allowed_sv.rename(columns={'MarketText': 'SalesVersionName'}, inplace=True)
    df_allowed_sv.drop_duplicates(subset='SalesVersion', keep='first', inplace=True)
    df_allowed_sv.drop(columns='TmpCode', inplace=True)

    df_allowed_sv['SalesVersionPrice'] = df_allowed_sv['ID'].map(df_pno_price.set_index('RelationID')['Price'])

    # Sort by price descending and return the names and prices
    df_allowed_sv = df_allowed_sv.sort_values(by='SalesVersionPrice', ascending=True)
    return df_allowed_sv[['ID', 'SalesVersion', 'SalesVersionName', 'SalesVersionPrice']]

def get_valid_engines(country, engine_cat, time):
    df_all_engines = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'En'), conditions=[f'CountryCode = {country}'])
    df_engines = filter_df_by_timestamp(df_all_engines, time)
    if engine_cat == '':
        other_engines = df_engines[df_engines['EngineCategory'].isna()]
        if other_engines.empty:
            DBOperations.instance.logger.info(f"No engines found for the given engine category {engine_cat}")
            return
        other_engines['EngineType'] = ''
        return other_engines.groupby('EngineType').agg({'Code': list}).reset_index()
    elif engine_cat.lower() == 'all':
        df_engines['EngineType'] = ''
        return df_engines.groupby('EngineType').agg({'Code': list}).reset_index()
    
    df_engines = df_all_engines[df_all_engines['EngineCategory'] == engine_cat]
    if df_engines.empty:
        DBOperations.instance.logger.info(f"No engines found for the given engine category {engine_cat}")
        return 
    
    df_engines['EngineType'] = df_engines['EngineType'].fillna(df_engines['EngineCategory'])
    
    # group by the new column and return the list of engines for each group
    return df_engines.groupby('EngineType').agg({'Code': list}).reset_index()

def get_valid_pnos(country, model, time, engines_types):
    df_all_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), conditions=[f'CountryCode = {country}', f'Model = {model}', f'Steering = 1'])
    df_pnos = filter_df_by_timestamp(df_all_pnos, time)
    if df_pnos.empty:
        DBOperations.instance.logger.info(f"No PNOs found for model {model}")

    # engines_types is a df. engines_types.Code is a list of engines for each row
    allowed_patrol_engines = engines_types.explode('Code')['Code'].unique()
    
    # filter pnos where Engine is in allowed_patrol_engines
    df_pno = df_pnos[df_pnos['Engine'].isin(allowed_patrol_engines)]
    return df_pno
