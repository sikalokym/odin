import pandas as pd
from src.database.services import get_engine_cats
from src.ingest.cpam.api import get_car_types, get_model_years

def is_valid_year(year, spec_market):
    """Check if year is valid.

    Args:
        year (str): Year to check
        years (list): List of valid years

    Returns:
        bool: True if year is valid, False otherwise
    """
    years = get_model_years(spec_market)
    return year in years['Years'] if years else 'CPAM internal error'

def is_valid_car_type(car_type, year, country_code):
    """Check if car type is valid.

    Args:
        car_type (str): Car type to check
        year (str): Model year

    Returns:
        bool: True if car type is valid, False otherwise
    """
    car_types = get_car_types(year, country_code)
    
    return car_type in [car['Type'] for car in car_types['DataRows']] if car_types else 'CPAM internal error'

def is_valid_engine_category(engine_category, year, country_code, model):
    """Check if engine category is valid.

    Args:
        engine_category (str): Engine category to check
        year (str): Model year
        country_code (str): Country code

    Returns:
        bool: True if engine category is valid, False otherwise
    """
    engine_cats = [cat.lower() for cat in get_engine_cats(country_code, year, model)]
    additional_cats = ['all', '']

    # Combine the lists
    all_cats = engine_cats + additional_cats

    # Check if engine_category is in all_cats
    return engine_category.lower() in all_cats

def excel_files_to_df(files):
    """Convert excel files to dataframes.

    Args:
        files (list): List of excel files

    Returns:
        list: List of dataframes
    """    # Read the Excel files into a pandas DataFrame
    df = pd.concat([pd.read_excel(file, dtype=str) for file in files])

    # Select the desired columns
    df = df[['Car Type', 'Engine', 'Sales Version', 'Body', 'Gearbox', 'Steering', 'Market Code', 'Color', 'Option', 'Upholstery', 'Package', 'MSRP', 'Price Before Tax', 'Date From', 'Date To']]

    # Return the modified DataFrame
    return df
