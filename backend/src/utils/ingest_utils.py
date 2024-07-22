import pandas as pd

from src.ingest.cpam.api import get_car_types, get_model_years
from src.database.services import get_engine_cats

# @author Hassan Wahba

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

def get_authorization_status(global_auth, market_auth, pnos=None):
    join_cols = market_auth.columns.tolist()
    merged_df = market_auth.merge(global_auth, on=join_cols, how='left', indicator=True)
    
    locally_authorized = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])
    
    merged_df = global_auth.merge(market_auth, on=join_cols, how='left', indicator=True)
    
    globally_authorized = merged_df[merged_df['_merge'] == 'both'].drop(columns=['_merge'])
    globally_unauthorized = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])

    authorized = pd.concat([globally_authorized, locally_authorized])
    if pnos is not None:
        unauthorized_all = filter_unauth_from_auth(globally_unauthorized, locally_authorized)
        unauthorized_expanded = fill_pnos(unauthorized_all, pnos)
        unauthorized = filter_unauth_from_auth(unauthorized_expanded, locally_authorized)
    else:
        unauthorized = globally_unauthorized
    
    return authorized, unauthorized

def fill_pnos(df, pnos):
    attributes = ['Model', 'Engine', 'SalesVersion', 'Steering', 'Gearbox', 'Body', 'MarketCode']
    df_non_att_cols = [col for col in df.columns.tolist() if col not in attributes]
    df_res = pd.DataFrame(columns=df.columns)
    for _, row in df.iterrows():
        conds = [f"{att} == '{row[att]}'" for att in attributes if not isinstance(row[att], str) or row[att].strip() != ""]
        df_filtered = pnos.query(' & '.join(conds))
        # take the non attribute columns from the row
        df_filtered = df_filtered[attributes]
        for col in df_non_att_cols:
            df_filtered[col] = row[col]
        df_res = pd.concat([df_res, df_filtered])
    return df_res

def filter_unauth_from_auth(df1, df2):
    """Get variant matches between two DataFrames.

    Args:
        df1 (DataFrame): First DataFrame
        df2 (DataFrame): Second DataFrame

    Returns:
        DataFrame: DataFrame containing df1 rows that are not in df2 based on the attributes
    """
    attributes = ['Model', 'Engine', 'SalesVersion', 'Steering', 'Gearbox', 'Body', 'MarketCode']
    all_cols = df2.columns.tolist()
    non_atts = [col for col in all_cols if col not in attributes and col not in ['StartDate', 'EndDate']]
    idxs = []
    allowed = []
    for _, row in df2.iterrows():
        conds = [f"{non_att} == '{row[non_att]}'" for non_att in non_atts]
        init_matches = df1.query(' & '.join(conds))
        if init_matches.empty:
            continue
        matches = init_matches[(init_matches['EndDate'] <= row['EndDate']) & (init_matches['StartDate'] >= row['StartDate'])]

        # Check each attribute
        for attr in attributes:
            if pd.isna(row[attr]):
                continue
            if not isinstance(row[attr], str):
                row[attr] = str(row[attr])
            
            if row[attr].strip() == "":
                continue
            
            matches = matches[(matches[attr] == str(row[attr]))]

        idxs += init_matches[~init_matches.index.isin(matches.index)].index.tolist()
        allowed += matches.index.tolist()
    
    idxs = list(set(idxs) - set(allowed))
    return df1.loc[idxs]
