import pandas as pd


def process_visa_df(df, cols):
    """
    Process the given DataFrame by performing various data cleaning and transformation operations.

    Args:
        df (pandas.DataFrame): The input DataFrame to be processed.
        cols (list): A list of column names to be included in the output DataFrame.

    Returns:
        pandas.DataFrame: The cleaned DataFrame containing only the specified columns.
    """

    # Convert 'Date From' and 'Date To' to datetime format if they are not already
    df['Date From'] = pd.to_datetime(df['Date From'])
    df['Date To'] = pd.to_datetime(df['Date To'])

    # Convert 'Date From' and 'Date To' to 'yyyyww' format
    df['Model Year'] = df['Model Year'].apply(lambda x: int(x))
    df['Date From'] = df['Date From'].apply(lambda x: int(x.strftime('%Y') + x.strftime('%U')))
    df['Date To'] = df['Date To'].apply(lambda x: int(x.strftime('%Y') + x.strftime('%U')))

    # Rename cols
    df = df.rename(columns={'Car Type': 'Model',
                            'Sales Version': 'SalesVersion',
                            'Market Code': 'MarketCode',
                            'Model Year': 'ModelYear',
                            'Option': 'Options',
                            'Date From': 'StartDate',
                            'Date To': 'EndDate',
                            'MSRP': 'Price',
                            'Price Before Tax': 'PriceBeforeTax'})

    # Convert 'Price' and 'PriceBeforeTax' to numeric
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').round(2).astype(float)
    df['PriceBeforeTax'] = pd.to_numeric(df['PriceBeforeTax'], errors='coerce').round(2).astype(float)

    # Return the cleaned DataFrame
    return df[cols]

def is_visa_file(excel):
    try:
        df = pd.read_excel(excel, usecols='A:AD', dtype=str)
        process_visa_df(df, ['Model'])
        return True
    except:
        return False
