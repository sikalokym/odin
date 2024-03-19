from src.database.db_operations import DBOperations


def get_sheet(ws, sales_versions, title):
    """
    Fetches options data and inserts it into the specified worksheet.

    Args:
        ws (Worksheet): The worksheet to insert the data into.
        sales_versions (DataFrame): The sales versions to fetch options data for.
        title (str): The title of the sheet.

    Returns:
        None
    """
    fetch_color_data(sales_versions)
    fetch_upholstery_data(sales_versions)

def fetch_upholstery_data(sales_versions):
    df_pno_upholstery = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'UPH'), columns=['ID', 'PNOID', 'Code', 'RuleName'], conditions=[f'CountryCode = {country}'])
    df_pno_upholstery_price = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'UPH_Custom'), columns=['RelationID', 'Price', 'PriceBeforeTax', 'CustomName'])

    sales_versions.rename(columns={'ID': 'TmpCode'}, inplace=True)
    df_pno_upholstery = df_pno_upholstery.merge(sales_versions[['TmpCode', 'SalesVersion', 'SalesVersionName']], left_on='PNOID', right_on='TmpCode', how='left')
    df_pno_upholstery.drop(columns='TmpCode', inplace=True)
    df_pno_upholstery_with_sv = df_pno_upholstery[df_pno_upholstery['SalesVersion'].notna()]
    # Replace ID with Price from df_pno_upholstery_price
    df_pno_upholstery_with_price = df_pno_upholstery_with_sv.merge(df_pno_upholstery_price, left_on='ID', right_on='RelationID', how='left')

    # Create the pivot table
    pivot_df = df_pno_upholstery_with_price.pivot_table(index=['Code', 'Price'], columns='SalesVersion', values='RuleName', aggfunc='first')

    # Concatenate Price and PriceBeforeTax
    df_pno_upholstery_with_price['Price'] = df_pno_upholstery_with_price.apply(lambda x: f"{x['Price']}/{x['PriceBeforeTax']}", axis=1)

    # Drop the now unneeded columns and duplicates
    df_pno_upholstery_with_price.drop(['ID', 'PNOID', 'RelationID', 'RuleName', 'SalesVersion', 'SalesVersionName', 'PriceBeforeTax'], axis=1, inplace=True)
    df_pno_upholstery_with_price.drop_duplicates(inplace=True)

    # Join the pivoted DataFrame with the original one. sort after code ascending
    result_df = df_pno_upholstery_with_price.join(pivot_df, on=['Code', 'Price']).sort_values(by='Code')

    result_df.to_csv('upholstery.csv', index=False)

    # return result_df
