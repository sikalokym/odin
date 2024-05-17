import pandas as pd
from src.storage import blob
from src.database.db_operations import DBOperations

def get_sap_price_list(name, partner_code, country, time):
    df_visa = blob.load_visa_file(name)
    assert not df_visa.empty, 'Visa file is empty'
    assert len(time) == 6, 'Invalid time format'
    conditions = [f'CountryCode = {country}',f'StartDate <= {time}', f'EndDate >= {time}']
    df_contract_partners = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'CP'), columns=['Code', 'PartnerName', 'Discount', 'Comment', 'StartDate', 'EndDate'], conditions=conditions)
    df_contract_partners.drop(columns=['StartDate', 'EndDate'], inplace=True)

    df_sap_price = df_visa.drop(columns=['MSRP', 'VAT', 'TAX1', 'TAX2'])
    df_sap_price = df_sap_price.rename(columns={'Price Before Tax': 'Retail Price'})
    df_sap_price['Date From'] = pd.to_datetime(df_sap_price['Date From'])
    df_sap_price['Date To'] = pd.to_datetime(df_sap_price['Date To'])

    df_sap_price['Date From'] = df_sap_price['Date From'].dt.strftime('%Y.%m.%d')
    df_sap_price['Date To'] = df_sap_price['Date To'].dt.strftime('%Y.%m.%d')

    df_sap_price['Sales Org.'] = '2481'
    df_sap_price['Structure week'] = ''
    df_sap_price['Transfer Price'].apply(lambda x: float(x)*0.74)
    df_sap_price['Active'] = 'A'
    if partner_code != 'All':
        df_contract_partners = df_contract_partners[df_contract_partners['Code'] == partner_code]
    dfs = []
    for _, row in df_contract_partners.iterrows():
        res_df = df_sap_price.copy()
        res_df['Wholesale Price'].apply(lambda x: float(x)*float(row['Discount']))
        res_df.name = f"{row['Code']}+#+{row['PartnerName']}"
        dfs.append(res_df)

    return dfs
