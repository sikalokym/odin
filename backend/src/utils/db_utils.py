import pandas as pd

pd.set_option('future.no_silent_downcasting', True)

def find_variant_matching_pno_ids(row, df_pno, attributes):
    """
    Find matching PNO IDs based on the given row and attributes.

    Args:
        row (pandas.Series): The row containing the data to match against.
        df_pno (pandas.DataFrame): The DataFrame containing the PNO data.
        attributes (list): A list of attribute names to match against.

    Returns:
        list: A list of matching PNO IDs.

    """
    # Start with filtering by dates
    matches = df_pno[(df_pno['EndDate'] > row['StartDate']) & (df_pno['StartDate'] < row['EndDate'])]

    # Check each attribute
    for attr in attributes:
        if pd.notna(row[attr]) and row[attr].strip() != "":
            matches = matches[(matches[attr] == row[attr])]

    if matches.empty:
        # TODO: create report
        return None

    # Return all matching PNO IDs
    return matches['ID'].tolist()

def find_matching_relation_ids(row, df_relation):
    """
    Find matching relation IDs based on the given row and dataframe.

    Parameters:
    - row: A pandas Series representing a row of data.
    - df_relation: A pandas DataFrame containing relation data.

    Returns:
    - A list of matching PNO IDs.

    This function filters the `df_relation` dataframe based on the start and end dates of the given `row`.
    It then further filters the matches based on the `Code` and `PNOID` columns of the `row`.
    Finally, it returns a list of matching PNO IDs from the filtered matches.
    If no matches are found, it returns None.
    """

    # Start with filtering by dates
    initial_matches = df_relation[(df_relation['EndDate'] > row['StartDate']) & (df_relation['StartDate'] < row['EndDate'])]

    # Add matches that have similar Code in the df_pno
    final_matches = initial_matches[(initial_matches['Code'] == row['Code']) & (initial_matches['PNOID'] == row['PNOID'])]

    # Return all matching PNO IDs
    ids = final_matches['ID'].tolist()
    if len(ids) == 0:
        return None
    return ids

def split_df(df):
    """
    Split the input DataFrame into multiple DataFrames based on the values in specific columns.

    Parameters:
    - df (pandas.DataFrame): The input DataFrame to be split.

    Returns:
    - df_pno_prices (pandas.DataFrame): DataFrame where certain columns are all filled and others are empty.
    - df_color (pandas.DataFrame): DataFrame where 'Color' column has a value.
    - df_option (pandas.DataFrame): DataFrame where 'Options' column has a value.
    - df_upholstery (pandas.DataFrame): DataFrame where 'Upholstery' column has a value.
    - df_package (pandas.DataFrame): DataFrame where 'Package' column has a value.
    """

    # DataFrame where certain columns are all filled and others are empty
    df_pno_prices = df[
        df[['Color', 'Options', 'Upholstery', 'Package']].isnull().all(axis=1)
    ]
    df_pno_prices = df_pno_prices.drop(columns=['Color', 'Options', 'Upholstery', 'Package'])

    # DataFrame where 'Color' column has a value
    df_color = df[df['Color'].notnull()]
    df_color = df_color.drop(columns=['Options', 'Upholstery', 'Package'])
    df_color = df_color.rename(columns={'Color': 'Code'})
    df_color = clean_code_column(df_color)
    df_color = sort_df_empty_to_filled(df_color)

    # DataFrame where 'Option' column has a value
    df_option = df[df['Options'].notnull()]
    df_option = df_option.drop(columns=['Color', 'Upholstery', 'Package'])
    df_option = df_option.rename(columns={'Options': 'Code'})
    df_option = clean_code_column(df_option)
    df_option = sort_df_empty_to_filled(df_option)

    # DataFrame where 'Upholstery' column has a value
    df_upholstery = df[df['Upholstery'].notnull()]
    df_upholstery = df_upholstery.drop(columns=['Color', 'Options', 'Package'])
    df_upholstery = df_upholstery.rename(columns={'Upholstery': 'Code'})
    df_upholstery = clean_code_column(df_upholstery)
    df_upholstery = sort_df_empty_to_filled(df_upholstery)

    # DataFrame where 'Package' column has a value
    df_package = df[df['Package'].notnull()]
    df_package = df_package.drop(columns=['Color', 'Options', 'Upholstery'])
    df_package = df_package.rename(columns={'Package': 'Code'})
    df_package = clean_code_column(df_package)
    df_package = sort_df_empty_to_filled(df_package)

    return df_pno_prices, df_color, df_option, df_upholstery, df_package

def clean_code_column(df):
    """
    Cleans the 'Code' column in the given DataFrame by removing redundancy and keeping only numbers and letters.

    Args:
        df (pandas.DataFrame): The DataFrame containing the 'Code' column to be cleaned.

    Returns:
        pandas.DataFrame: The DataFrame with the 'Code' column cleaned.

    Example:
        >>> df = pd.DataFrame({'Code': ['A-123', 'B-456', 'C-789']})
        >>> cleaned_df = clean_code_column(df)
        >>> print(cleaned_df)
           Code
        0   A123
        1   B456
        2   C789
    """
    df['Code'] = df['Code'].str.replace('-', '')
    return df

def sort_df_empty_to_filled(df):
    """
    Sorts a DataFrame by the number of empty values in each row.

    Args:
        df (pandas.DataFrame): The DataFrame to be sorted.

    Returns:
        pandas.DataFrame: The sorted DataFrame.

    Example:
        >>> df = pd.DataFrame({'A': ['', 'value1', 'value2'],
        ...                    'B': ['-', 'value3', 'value4'],
        ...                    'C': ['--', 'value5', 'value6']})
        >>> sorted_df = sort_df_empty_to_filled(df)
        >>> print(sorted_df)
              A       B       C
        0    --       -        
        1          value3  value5
        2  value1  value4  value6
    """
    
    df.replace(['', '-', '--'], None, inplace=True)

    # Calculate the number of NaNs in each row and create a new column
    df['NaN_Count'] = df.isna().sum(axis=1)

    # Sort the DataFrame based on 'NaN_Count' in descending order
    df_sorted = df.sort_values(by='NaN_Count', ascending=False)

    # Optionally, drop the 'NaN_Count' column if it's no longer needed
    df_sorted.drop('NaN_Count', axis=1, inplace=True)

    return df_sorted

def df_from_datarows(datarows, dr_columns):
    """
    Convert a list of data rows into a pandas DataFrame.

    Args:
        datarows (list): A list of data rows.
        dr_columns (list): A list of column names for the data rows.

    Returns:
        pandas.DataFrame: A DataFrame containing the converted data rows.

    Example:
        datarows = [
            {"VariantRules": [{"variant": "A", "value": 1}, {"variant": "B", "value": 2}]},
            {"VariantRules": [{"variant": "C", "value": 3}, {"variant": "D", "value": 4}]}
        ]
        dr_columns = ["variant", "value"]
        df = df_from_datarows(datarows, dr_columns)
        print(df)
    """

    rows = [
        {**{drc: datarow[drc] for drc in dr_columns}, **variant}
        for datarow in datarows
        for variant in datarow["VariantRules"]
    ]

    # Convert the list of dictionaries directly to a DataFrame
    df = pd.DataFrame(rows)
    df['StartDate'] = df['StartDate'].astype(int)
    df['EndDate'] = df['EndDate'].astype(int)
    return df

def df_from_package_datarows(datarows):
    flat_data = []

    for item in datarows:
        code = item[0]['Code']
        text = item[1]['Title']
        
        for subitem in item[2:]:
            variant_rules = subitem['VariantRules']['VariantRules']
            content = subitem['Content'][0]['Content']
            
            for vr in variant_rules:
                for ct in content:
                    flat_data.append({
                        'Code': code,
                        'Title': text,
                        **ct,
                        **vr
                    })

    # Create the DataFrame
    df = pd.DataFrame(flat_data)
    return df

def get_pno_ids_from_variants(df_pno, df_variants, is_relation=False):
    """
    Retrieves PNO IDs from variants based on matching attributes.

    Args:
        df_pno (DataFrame): The DataFrame containing PNO data.
        df_variants (DataFrame): The DataFrame containing variant data.
        is_relation (bool, optional): Specifies whether to use 'RelationID' or 'PNOID' as the PNO code. 
            Defaults to False.

    Returns:
        tuple: A tuple containing two DataFrames:
            - df_pno_found: The DataFrame with matched PNO IDs, excluding the specified attributes.
            - pno_na: The DataFrame with unmatched PNO IDs, excluding the PNO code.

    """
    df = df_variants.copy()
    attributes = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode']
    
    PNOCode = 'RelationID' if is_relation else 'PNOID'

    df.insert(0, PNOCode, -1)
    
    df[PNOCode] = df.apply(lambda row: find_variant_matching_pno_ids(row, df_pno, attributes), axis=1)
    df = df.explode(PNOCode)
    
    df_pno_found = df[df[PNOCode].notna()]
    pno_na = df[df[PNOCode].isna()]
    return df_pno_found.drop(attributes, axis=1), pno_na.drop(PNOCode, axis=1)

def get_relation_ids(df_relation, df_assigned):
    """
    Retrieves relation IDs based on matching attributes.

    Args:
        df_relation (DataFrame): The DataFrame containing relation data.
        df_assigned (DataFrame): The DataFrame containing assigned data.

    Returns:
        DataFrame: The DataFrame with matched relation IDs.
    """
    df = df_assigned.copy()
    df.insert(0, 'RelationID', '')
    df['RelationID'] = df.apply(lambda row: find_matching_relation_ids(row, df_relation), axis=1)
    filtered_df = df[df['RelationID'].notna()]
    
    expanded_df = filtered_df.explode('RelationID')
    final_df = expanded_df.drop(['PNOID', 'Code'], axis=1)
    return final_df
    
def filter_df_by_timestamp(df, timestamp):
    """
    Filters a DataFrame based on a given timestamp.

    Args:
        df (pandas.DataFrame): The DataFrame to be filtered.
        timestamp (datetime): The timestamp to filter the DataFrame.

    Returns:
        pandas.DataFrame: The filtered DataFrame.

    """
    return df[(df['StartDate'] <= timestamp) & (df['EndDate'] >= timestamp)]

def filter_df_by_model_year(df, model_year):
    """
    Filters a DataFrame based on the given model year.

    Args:
        df (pandas.DataFrame): The DataFrame to be filtered.
        model_year (int): The model year to filter by.

    Returns:
        pandas.DataFrame: The filtered DataFrame.

    """
    if isinstance(model_year, str):
        if not model_year.isdigit():
            raise ValueError("Model year must be a valid integer.")
        if len(model_year) != 4:
            raise ValueError("Model year must be in the format YYYY.")
        model_year = int(model_year)
        if not model_year:
            df['ModelYear'] = df['StartDate'].apply(get_model_year_from_date)
            return df
    elif not isinstance(model_year, int):
        raise ValueError("Model year must be an integer or string.")
    return df[(df['StartDate'].apply(get_model_year_from_date) == model_year) | (df['EndDate'].apply(get_model_year_from_date) == model_year)]
    

def get_model_year_from_date(date):
    """
    Returns the model year based on the given date.
    
    Parameters:
        date (int): The date in the format YYYYWW, where YYYY represents the year and WW represents the week.
        
    Returns:
        int: The model year corresponding to the given date.
    """
    year, week = divmod(date, 100)
    if week < 17:
        return year
    return year + 1

def format_float_string(float_string):
    """
    Formats a float string by adding thousands separator (dot) and two decimal places.
    
    Args:
        float_string (str): The float string to be formatted.
        
    Returns:
        str: The formatted float string.
        
    Example:
        >>> format_float_string('1234567.890')
        '1.234.567,89'
    """
    
    # Convert string to float to ensure correct handling
    float_value = float(float_string)
    
    # Format with thousands separator (dot) and two decimal places
    # Note: The format uses a comma for the decimal separator as per the locale setting
    formatted_string = f"{float_value:,.2f}"
    
    # Replace commas with dots and dots with commas
    formatted_string = formatted_string.replace(",", "X").replace(".", ",").replace("X", ".")
    
    return formatted_string
