import pandas as pd
from src.ingest.visa_files import preprocess
from src.database.db_operations import DBOperations
from src.utils.sql_logging_handler import logger
from src.utils.db_utils import get_column_map


def ingest_visa_file(visa_excel, country_code):
    try:
        df_raw, df_visa = preprocess.is_visa_file(visa_excel)
        df_raw['VisaFile'] = visa_excel.filename.rstrip('.xlsx')
        df_raw['CountryCode'] = f'{country_code}'
        c_map = get_column_map()
        df_raw.columns = [c_map.get(col, col) for col in df_raw.columns]
        DBOperations.instance.upsert_data_from_df(df_raw, DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), df_raw.columns.tolist(), df_raw.columns.tolist())
        df_visa.insert(7, 'CountryCode', country_code)
        ingest_visa_data(country_code, df_visa)
        return "File uploaded successfully", 200
    except Exception as e:
        logger.error(f"Failed to upload visa file: {e}", extra={'country_code': country_code})
        return str(e), 400

def ingest_visa_data(country_code, df_processed):
    if df_processed is None:
        df_raw = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), conditions=[f"CountryCode = '{country_code}'"])
        df_processed = preprocess.process_visa_df(df_raw)
        df_processed.insert(7, 'CountryCode', country_code)
    if df_processed.empty:
        return
    
    def process_and_upsert(df, condition_col, drop_cols, df_tmp):
        if condition_col:
            filtered_df = df[df[condition_col] != '']
        else:
            # Filter where all drop_cols are empty strings at the same time
            mask = (df[drop_cols] == '').all(axis=1)
            filtered_df = df[mask]

        filtered_df = filtered_df.drop(columns=drop_cols)
        df_tmp = pd.concat([df_tmp, filtered_df])
        return df_tmp

    df_res = pd.DataFrame()
    # Processing different cases
    df_res = process_and_upsert(df_processed, None, ['Color', 'Options', 'Upholstery', 'Package'], df_res)
    df_res = process_and_upsert(df_processed, 'Color', ['Options', 'Upholstery', 'Package'], df_res)
    df_res = process_and_upsert(df_processed, 'Options', ['Color', 'Upholstery', 'Package'], df_res)
    df_res = process_and_upsert(df_processed, 'Upholstery', ['Color', 'Options', 'Package'], df_res)
    df_res = process_and_upsert(df_processed, 'Package', ['Color', 'Options', 'Upholstery'], df_res)
    DBOperations.instance.assign_prices_from_visa_dataframe(country_code, df_res)

def get_available_visa_files(country_code, model_year=None, visa_columns=None):
    conditions = [f"CountryCode = '{country_code}'"]
    if model_year is not None:
        conditions.append(f"ModelYear = '{model_year}'")
    raw_visa_files = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), columns=visa_columns, conditions=conditions)

    return raw_visa_files
