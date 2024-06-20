import pandas as pd
from src.database.services import get_engine_cats
from src.ingest.cpam.api import get_car_types, get_model_years

def is_valid_year(year, country_code):
    """Check if year is valid.

    Args:
        year (str): Year to check
        years (list): List of valid years

    Returns:
        bool: True if year is valid, False otherwise
    """
    years = get_model_years(country_code)
    if not years or years == []:
        return 'CPAM internal error'
    return year in years['Years']

def is_valid_car_type(car_type, year, country_code):
    """Check if car type is valid.

    Args:
        car_type (str): Car type to check
        year (str): Model year

    Returns:
        bool: True if car type is valid, False otherwise
    """
    car_types = get_car_types(year, country_code)
    
    if not car_types or car_types == []:
        return 'CPAM internal error'
    return car_type in [car['Type'] for car in car_types['DataRows']]

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
