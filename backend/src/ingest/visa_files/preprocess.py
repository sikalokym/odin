import pandas as pd

from src.utils.db_utils import get_column_map


def process_visa_df(df):
    """
    Process the given DataFrame by performing various data cleaning and transformation operations.

    Args:
        df (pandas.DataFrame): The input DataFrame to be processed.
        cols (list): A list of column names to be included in the output DataFrame.

    Returns:
        pandas.DataFrame: The cleaned DataFrame containing only the specified columns.
    """
    df = df.copy()
    cols = ['Model', 'Engine', 'SalesVersion', 'Body', 'Gearbox', 'Steering', 'MarketCode', 'ModelYear', 'StartDate', 'EndDate', 'Color', 'Options', 'Upholstery', 'Package', 'Price', 'PriceBeforeTax']

    # Convert 'Date From' and 'Date To' to datetime format if they are not already
    df['DateFrom'] = pd.to_datetime(df['DateFrom'])
    df['DateTo'] = pd.to_datetime(df['DateTo'])

    # Convert 'Date From' and 'Date To' to 'yyyyww' format
    df['ModelYear'] = df['ModelYear'].apply(lambda x: int(x))
    df['DateFrom'] = df['DateFrom'].apply(lambda x: int(x.strftime('%Y') + x.strftime('%U')))
    df['DateTo'] = df['DateTo'].apply(lambda x: int(x.strftime('%Y') + x.strftime('%U')))

    # Rename cols
    df = df.rename(columns={'CarType': 'Model',
                            'DateFrom': 'StartDate',
                            'DateTo': 'EndDate',
                            'MSRP': 'Price'})

    # Convert 'Price' and 'PriceBeforeTax' to numeric
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').round(2).astype(float)
    df['PriceBeforeTax'] = pd.to_numeric(df['PriceBeforeTax'], errors='coerce').round(2).astype(float)

    # Return the cleaned DataFrame
    return df[cols]

def is_visa_file(excel):
    try:
        df = pd.read_excel(excel, usecols='A:AD', dtype=str)
        # replace nan values with empty string
        df = df.replace({pd.NA: ''})
        c_map = get_column_map()
        assert len(set(c_map.keys()) - set(df.columns)) == 2, "Column sets do not match"
        df.columns = [c_map.get(col, col) for col in df.columns]
        df_res = process_visa_df(df)
        return df, df_res
    except Exception as e:
        print(f"Assertion error: {e}")
        return False
