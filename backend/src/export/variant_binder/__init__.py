from io import BytesIO
import numpy as np
from openpyxl import Workbook
from src.database.db_operations import DBOperations
from src.export.variant_binder import prices_sheet, options_sheet, upholstery_colors_sheet, packages_sheet, sales_versions_sheet, tiers_sheet
from src.utils.db_utils import filter_df_by_timestamp, get_model_year_from_date


def extract_variant_binder(country, model, engines_types, time):
    wb = Workbook()

    # Remove the default sheet created
    default_sheet = wb.active
    wb.remove(default_sheet)

    try:
        valid_engines = get_valid_engines(country, engines_types, time)
        valid_pnos = get_valid_pnos(country, model, time, valid_engines)
        sales_versions = get_sales_versions(country, valid_pnos, time)
        title = get_model_name(country, model, time)
    except Exception as e:
        DBOperations.instance.logger.error(f"Error getting VB Data: {e}")
        raise Exception(f"Error getting VB Data: {e}")

    if valid_pnos.empty or sales_versions.empty or valid_engines.empty:
        DBOperations.instance.logger.info(f"No data found for model {model} and engine category {engines_types} at time {time}")
        return None

    try:
        ws_1 = wb.create_sheet("Preise")
        prices_sheet.get_sheet(ws_1, valid_pnos, sales_versions.copy(), title, time, valid_engines, country)
    except Exception as e:
        DBOperations.instance.logger.error(f"Error creating sheet: {e}")
    try:
        ws_2 = wb.create_sheet("Serienausstattung")
        sales_versions_sheet.get_sheet(ws_2, sales_versions.copy(), title, country, time)
    except Exception as e:
        DBOperations.instance.logger.error(f"Error creating sheet: {e}")
    try:
        ws_3 = wb.create_sheet("Pakete")
        packages_sheet.get_sheet(ws_3, sales_versions.copy(), title, time)
    except Exception as e:
        DBOperations.instance.logger.error(f"Error creating sheet: {e}")
    try:
        ws_4 = wb.create_sheet("Polster & Farben")
        upholstery_colors_sheet.get_sheet(ws_4, sales_versions.copy(), title, time)
    except Exception as e:
        DBOperations.instance.logger.error(f"Error creating sheet: {e}")
    try:
        ws_5 = wb.create_sheet("Optionen")
        df_rad = options_sheet.get_sheet(ws_5, sales_versions.copy(), title, time)
        ws_6 = wb.create_sheet("Räder")
        tiers_sheet.get_sheet(ws_6, sales_versions.copy(), title, df_rad)
    except Exception as e:
        DBOperations.instance.logger.error(f"Error creating sheet: {e}")

    model_year = get_model_year_from_date(time)
    time = str(time)
    vb_title = f"{title.replace(' ', '')}_VB_{engines_types}_{model_year}_{time[:4]}w{time[4:]}.xlsx"
    # wb.save(vb_title)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output, vb_title
    
def get_model_name(country, model, time):
    models = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'Typ'), ['MarketText', 'CustomName', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}', f'Code = {model}'])

    # filter models where StartDate and End Data wrap the current time for the given model
    df_model = filter_df_by_timestamp(models, time)
    
    df_model['Title'] = df_model['CustomName'].combine_first(df_model['MarketText'])

    title = df_model.iloc[0]['Title']
    if title:
        return title
    else:
        raise Exception(f"No model found for model {model}")

def get_sales_versions(country, pnos, time):
    df_sv = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'SV'), conditions=[f'CountryCode = {country}'])
    df_pno_price = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'PNO_Custom'))
    if df_pno_price.empty:
        raise Exception("No price data found")
    df_sv = filter_df_by_timestamp(df_sv, time)
    df_sv.rename(columns={'Code': 'TmpCode'}, inplace=True)

    df_allowed_sv = pnos.merge(df_sv[['TmpCode', 'MarketText', 'CustomName']], left_on='SalesVersion', right_on='TmpCode', how='left')
    df_allowed_sv['SalesVersionName'] = df_allowed_sv['CustomName'].combine_first(df_allowed_sv['MarketText'])
    df_allowed_sv.drop_duplicates(subset='SalesVersion', keep='first', inplace=True)

    df_allowed_sv['SalesVersionPrice'] = df_allowed_sv['ID'].map(df_pno_price.set_index('RelationID')['Price'])
    df_allowed_sv = df_allowed_sv[['ID', 'SalesVersion', 'SalesVersionName', 'SalesVersionPrice']]

    # sort the sales versions by price
    df_allowed_sv = df_allowed_sv.sort_values('SalesVersionPrice', ascending=True)

    # group by SalesVersionName name's first word and represent each group with its maximum price and sort on price ascending and return the names and prices
    df_allowed_sv['SalesVersionNameGroup'] = df_allowed_sv['SalesVersionName'].str.split().str[0]
    df = df_allowed_sv.groupby('SalesVersionNameGroup').agg({'SalesVersionName': list, 'SalesVersionPrice': 'max'}).sort_values('SalesVersionPrice', ascending=True)
    # explode the list of names to get the names sorted by price
    sorted_sv_names = df.explode('SalesVersionName')['SalesVersionName'].tolist()

    # now we have the names of the sales versions sorted by price
    # sort the original df by the order of the names in the sorted df
    df_final = df_allowed_sv.set_index('SalesVersionName').loc[sorted_sv_names].reset_index()
    df_final.drop(columns=['SalesVersionNameGroup'], inplace=True)

    return df_final

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
    
    df_engines = df_engines[df_engines['EngineCategory'] == engine_cat]
    if df_engines.empty:
        DBOperations.instance.logger.info(f"No engines found for the given engine category {engine_cat}")
        return 
    
    df_engines['EngineType'] = df_engines['EngineType'].replace('', np.nan).fillna(df_engines['EngineCategory'])
    
    # group by the new column and return the list of engines for each group
    return df_engines.groupby('EngineType').agg({'Code': list, 'CustomName': list, 'Performance': list}).reset_index()

def get_valid_pnos(country, model, time, engines_types):
    conditions=[f'CountryCode = {country}', f'Model = {model}', f'Steering = 1']
    allowed_engines = engines_types['Code'].explode('Code').unique().tolist()
    if not allowed_engines:
        DBOperations.instance.logger.info(f"No engines found for the given engine category {engines_types}")
        return
    elif len(allowed_engines) == 1:
        conditions.append(f'Engine = {allowed_engines[0]}')
    else:
        conditions.append(f'Engine in {tuple(allowed_engines)}')

    df_all_pnos = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), conditions=conditions)
    df_pnos = filter_df_by_timestamp(df_all_pnos, time)
    if df_pnos.empty:
        DBOperations.instance.logger.info(f"No PNOs found for model {model}")
        raise Exception(f"No PNOs found for model {model}")

    return df_pnos
