from src.ingest.visa_files import preprocess
import src.storage.blob as blob
from src.database.db_operations import DBOperations

import configparser

from src.utils.db_utils import get_column_map

config = configparser.ConfigParser()
config.read('config/data_model.cfg')

def upload_visa_file(visa_excel, spec_markt):
    """
    Uploads a visa file to the system and ingests the visa data.
    
    Args:
        visa_excel (str): The path to the visa Excel file.
    """
    try:
        preprocess.is_visa_file(visa_excel)
        blob.add_visa_file(visa_excel, spec_markt)
        ingest_visa_data(spec_markt)
        return {"message": "File uploaded successfully"}, 200
    except Exception as e:
        print(f"Failed to upload visa file: {e}")
        return {"error": str(e)}, 400

def ingest_visa_data(spec_markt):
    """
    Ingests visa data from a blob and performs data processing and database operations.

    This function loads visa data from a blob, preprocesses the data, and performs database operations
    to upsert the processed data into the specified table. It splits the dataframe based on the values
    in the 'Color', 'Options', 'Upholstery', and 'Package' columns and performs upsert operations for
    each split dataframe.

    Returns:
        None
    """
    df_visa = blob.load_visa_files(spec_markt)
    c_map = get_column_map()
    df_visa.columns = [c_map[col] for col in df_visa.columns]
    
    DBOperations.instance.upsert_data_from_df(df_visa, config.get('RELATIONS', 'RAW_VISA'), df_visa.columns.tolist(), df_visa.columns.tolist())
    
    columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'ModelYear', 'StartDate', 'EndDate', 'Color', 'Options', 'Upholstery', 'Package', 'Price', 'PriceBeforeTax']
    df_processed = preprocess.process_visa_df(df_visa, columns)

    df_processed.insert(7, 'CountryCode', spec_markt)
    # Split the dataframe based on the values in the 'Color', 'Options', 'Upholstery', and 'Package' columns
    df_pno = df_processed[df_processed['Color'].isna() & df_processed['Options'].isna() & df_processed['Upholstery'].isna() & df_processed['Package'].isna()]
    df_pno = df_pno.drop(columns=['Color', 'Options', 'Upholstery', 'Package'])
    columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate', 'EndDate', 'Price', 'PriceBeforeTax']
    conditional_columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate']
    DBOperations.instance.upsert_data_from_df(df_pno, config.get('RELATIONS', 'VISA'), columns, conditional_columns)

    df_color = df_processed[df_processed['Color'].notna()]
    df_color = df_color.drop(columns=['Options', 'Upholstery', 'Package'])
    columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate', 'EndDate', 'Color', 'Price', 'PriceBeforeTax']
    conditional_columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate', 'Color']
    DBOperations.instance.upsert_data_from_df(df_color, config.get('RELATIONS', 'VISA'), columns, conditional_columns)

    df_options = df_processed[df_processed['Options'].notna()]
    df_options = df_options.drop(columns=['Color', 'Upholstery', 'Package'])
    columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate', 'EndDate', 'Options', 'Price', 'PriceBeforeTax']
    conditional_columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate', 'Options']
    DBOperations.instance.upsert_data_from_df(df_options, config.get('RELATIONS', 'VISA'), columns, conditional_columns)

    df_upholstery = df_processed[df_processed['Upholstery'].notna()]
    df_upholstery = df_upholstery.drop(columns=['Color', 'Options', 'Package'])
    columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate', 'EndDate', 'Upholstery', 'Price', 'PriceBeforeTax']
    conditional_columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate', 'Upholstery']
    DBOperations.instance.upsert_data_from_df(df_upholstery, config.get('RELATIONS', 'VISA'), columns, conditional_columns)

    df_package = df_processed[df_processed['Package'].notna()]
    df_package = df_package.drop(columns=['Color', 'Options', 'Upholstery'])
    columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate', 'EndDate', 'Package', 'Price', 'PriceBeforeTax']
    conditional_columns = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'CountryCode', 'ModelYear', 'StartDate', 'Package']
    DBOperations.instance.upsert_data_from_df(df_package, config.get('RELATIONS', 'VISA'), columns, conditional_columns)
    assign_prices(spec_markt)

def assign_prices(country_code):
    """
    Assigns prices from the Visa dataframe using DBOperations instance.
    """
    DBOperations.instance.assign_prices_from_visa_dataframe(country_code)

def get_available_visa_files(country_code, model_year):
    """
    Loads the list of available Visa files from the specified container.

    Args:
        country_code (str): The country code to filter the blob names.

    Returns:
        list: A list of blob names without the file extensions.
    """
    raw_visa_files = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), columns=['VisaFile', 'CarType'], conditions=[f"CountryCode = '{country_code}'", f"ModelYear = '{model_year}'"])
    c_map = get_column_map()
    
    # flip the dictionary
    c_map = {v: k for k, v in c_map.items()}
    raw_visa_files.columns = [c_map[col] for col in raw_visa_files.columns]
    return raw_visa_files
