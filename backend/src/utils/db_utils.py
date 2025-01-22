import pandas as pd
import numpy as np

# @author Hassan Wahba

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
        if pd.isna(row[attr]):
            continue
        if not isinstance(row[attr], str):
            row[attr] = str(row[attr])
        
        if row[attr].strip() == "":
            continue
        
        matches = matches[(matches[attr] == str(row[attr]))]

    if matches.empty:
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
    df_color['Code'] = df_color['Code'].str.slice(stop=3)
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
    df_upholstery['Code'] = df_upholstery['Code'].str.slice(stop=4)
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
        >>> df = pd.DataFrame({'A': ['', '--', 'value1'],
        ...                    'B': ['-', 'value2', 'value3'],
        ...                    'C': ['value4', 'value5', 'value6']})
        >>> sorted_df = sort_df_empty_to_filled(df)
        >>> print(sorted_df)
              A       B       C
        0                  value4
        1          value2  value5
        2  value1  value3  value6
    """
    
    df = df.replace(['', '-', '--'], None)

    # Calculate the number of NaNs in each row and create a new column
    df['NaN_Count'] = df.isna().sum(axis=1)

    # Sort the DataFrame based on 'NaN_Count' in descending order
    df_sorted = df.sort_values(by='NaN_Count', ascending=False)

    # Optionally, drop the 'NaN_Count' column if it's no longer needed
    df_sorted = df_sorted.drop('NaN_Count', axis=1)

    return df_sorted

def df_from_datarows(datarows, dr_columns=None):
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
    if len(datarows) == 0:
        return pd.DataFrame()
    if dr_columns is None:
        return pd.DataFrame(datarows)

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
    return df.fillna('')

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
    not_found_df = df[df['RelationID'].isna()]
    not_found_df = not_found_df.drop('RelationID', axis=1)
    
    expanded_df = filtered_df.explode('RelationID')
    final_df = expanded_df.drop(['PNOID', 'Code'], axis=1)
    return final_df, not_found_df
    
def filter_df_by_timestamp(df, timestamp):
    """
    Filters a DataFrame based on a given timestamp.

    Args:
        df (pandas.DataFrame): The DataFrame to be filtered.
        timestamp (datetime): The timestamp to filter the DataFrame.

    Returns:
        pandas.DataFrame: The filtered DataFrame.

    """
    if df.empty:
        return df
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
    df = df.copy()
    if isinstance(model_year, str):
        if not model_year.isdigit():
            raise ValueError("Model year must be a valid integer.")
        model_year = int(model_year)
        df['ModelYear'] = df['StartDate'].apply(get_model_year_from_date)
        if not model_year:
            return df
        else:
            return df[df['ModelYear'] == model_year].drop(columns=['ModelYear'])
    elif not isinstance(model_year, int):
        raise ValueError("Model year must be an integer or string.")
    return df[((df['StartDate'].apply(get_model_year_from_date) <= model_year) & (df['EndDate'].apply(get_model_year_from_date) >= model_year)) | (df['StartDate'].apply(get_model_year_from_date) == model_year) | (df['EndDate'].apply(get_model_year_from_date) == model_year)]
    
def filter_model_year_by_translation(df, conditional_columns):
    """
    Filters a DataFrame based on the model year and translation.

    Args:
        df (pandas.DataFrame): The DataFrame to be filtered.
        conditional_columns (list): A list of columns to filter by.
    Returns:
        pandas.DataFrame: The filtered DataFrame.
    """

    if 'ModelYear' in df.columns:
        df = df.sort_values('StartDate', ascending=False).drop_duplicates(['Code', 'ModelYear'], keep='first')
        # filter based on number of unique entries in conditional columns
        df['TmpModelYear'] = df['Code'].apply(lambda x: '' if df[df['Code'] == x][conditional_columns].nunique().max() <= 1 else None)
        df['ModelYear'] = df['TmpModelYear'].combine_first(df['ModelYear'])
        df = df.drop(columns=['TmpModelYear'])
    else:
        df = df.sort_values('StartDate', ascending=False).drop_duplicates('Code', keep='first')
    return df

def get_model_year_from_date(date):
    """
    Returns the model year based on the given date.
    
    Parameters:
        date (int): The date in the format YYYYWW, where YYYY represents the year and WW represents the week.
        
    Returns:
        int: The model year corresponding to the given date.
    """
    if date == 0:
        return 0
    elif not date:
        return 9999
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
    if float_string is None or float_string == '' or float_string == 'nan':
        return 'Not Assigned. Check Visa File'
    try:
        # Convert string to float to ensure correct handling
        float_value = float(float_string)
        if np.isnan(float_value):
            return 'Not Assigned. Check Visa File'
    except ValueError:
        return 'Not Assigned. Check Visa File'
    
    # Format with thousands separator (dot) and two decimal places
    # Note: The format uses a comma for the decimal separator as per the locale setting
    formatted_string = f"{float_value:,.2f}"
    
    # Replace commas with dots and dots with commas
    formatted_string = formatted_string.replace(",", "X").replace(".", ",").replace("X", ".")
    
    return formatted_string

def log_df(df, msg_prefix, callable_logger, country_code=None):
    """
    Logs DataFrame rows in batch to reduce the number of log entries.
    Each DataFrame row will be concatenated into a single large string, which is then logged at once.
    This reduces the number of logging calls and can significantly improve performance.

    Parameters:
    - df (pd.DataFrame): The DataFrame to log.
    - msg_prefix (str): A string prefix for each log message.
    - callable_logger (callable): A logging function.
    - country_code (str, optional): Country code to include in the log. If not provided,
      attempts to extract it from the DataFrame's 'CountryCode' column.

    Raises:
    - KeyError: If 'country_code' is not supplied and 'CountryCode' column is missing in the DataFrame.
    """
    if df.empty:
        return
    if country_code is None:
        try:
            country_code = df['CountryCode'].iloc[0]
        except KeyError:
            return

    # Initialize message list
    messages = []
    for _, row in df.iterrows():
        msg = [msg_prefix]
        msg.extend(f"{col}: {val}" for col, val in row.items())
        messages.append(', '.join(msg))

    # Combine all messages into one large string and log it
    full_message = "\n".join(messages)
    callable_logger(full_message, extra={'country_code': country_code})


def get_column_map(reverse=False):
    """
    Returns a dictionary mapping the old column names of visa files to the new column names.

    Returns: 
        dict: A dictionary mapping the old column names to the new column names.

    """
    column_map = {
        'Active': 'Active',
        'Sales Org.': 'SalesOrg',
        'Distr. Ch.': 'DistrCh',
        'Price List': 'PriceList',
        'Dealer Group': 'DealerGroup',
        'Country': 'Country',
        'Car Type': 'CarType',
        'Engine': 'Engine',
        'Sales Version': 'SalesVersion',
        'Body': 'Body',
        'Gearbox': 'Gearbox',
        'Steering': 'Steering',
        'Market Code': 'MarketCode',
        'Model Year': 'ModelYear',
        'Structure week': 'StructureWeek',
        'Date From': 'DateFrom',
        'Date To': 'DateTo',
        'Currency': 'Currency',
        'Color': 'Color',
        'Option': 'Options',
        'Upholstery': 'Upholstery',
        'Package': 'Package',
        'S-Note': 'SNote',
        'MSRP': 'MSRP',
        'TAX2': 'TAX2',
        'VAT': 'VAT',
        'TAX1': 'TAX1',
        'Price Before Tax': 'PriceBeforeTax',
        'Wholesale Price': 'WholesalePrice',
        'Transfer Price': 'TransferPrice',
        'VisaFile': 'VisaFile',
        'CountryCode': 'CountryCode'
    }
    if reverse:
        return {v: k for k, v in column_map.items()}
    return column_map

def fill_custom_name(group):
    """
    Fills missing values in the 'CustomName' column of a DataFrame group based on its contents.

    This function examines the 'CustomName' column in a provided DataFrame group. If there is exactly one unique,
    non-null value in this column, it fills all missing (NaN) entries in the column with this unique value. If there
    are zero or multiple unique non-null values, it fills the missing entries with an empty string.

    Parameters:
    - group (pd.DataFrame): The DataFrame group containing the 'CustomName' column to be processed.

    Returns:
    - pd.Series: The 'CustomName' column with missing values filled.

    """
    unique_not_null = group['CustomName'].dropna().unique()
    if len(unique_not_null) == 1:
        return group['CustomName'].fillna(unique_not_null[0])
    else:
        return group['CustomName'].fillna('')

def validate_and_format_date(date_str, default_date):
    """
    Validates and formats a date string by extracting the date part from a datetime string.

    This function checks if the provided date string is None or empty. If it is, the function returns a default date.
    Otherwise, it attempts to split the datetime string by 'T' to isolate and return just the date part.

    Parameters:
    - date_str (str): The date string in ISO 8601 format (e.g., '2020-01-01T12:00:00').
    - default_date (str): The default date string to return if `date_str` is None or empty.

    Returns:
    - str: The formatted date string or the default date if the original string is invalid.

    Example:
    ```python
    # Example usage
    formatted_date = validate_and_format_date('2020-01-01T15:30:00', '1900-01-01')
    print(formatted_date)  # Outputs: '2020-01-01'
    
    # Example with invalid input
    formatted_date = validate_and_format_date('', '1900-01-01')
    print(formatted_date)  # Outputs: '1900-01-01'
    ```
    """
    if (date_str is None) or (date_str == ''):
        return default_date
    return date_str.split('T')[0]

def get_last_week_date():
    """
    Get last weeks date in the format YYYYWW.
    """
    week = pd.Timestamp.now().week - 1
    year = pd.Timestamp.now().year
    if week == 0:
        year -= 1
        week = 52
    return year * 100 + week
