import pandas as pd
from src.storage import blob

def get_sap_price_list(name):
    df_sap_price, df_sap_matrix = _get_data(name)
    df_sap_price = df_sap_price.drop(columns=['MSRP', 'VAT', 'TAX1', 'TAX2'])
    df_sap_price = df_sap_price.rename(columns={'Price Before Tax': 'Retail Price'})
    df_sap_price['Date From'] = pd.to_datetime(df_sap_price['Date From'])
    df_sap_price['Date To'] = pd.to_datetime(df_sap_price['Date To'])

    df_sap_price['Date From'] = df_sap_price['Date From'].dt.strftime('%Y.%m.%d')
    df_sap_price['Date To'] = df_sap_price['Date To'].dt.strftime('%Y.%m.%d')

    df_sap_price['Sales Org.'] = '2481'
    df_sap_price['Structure week'] = ''
    df_sap_price['Transfer Price'].apply(lambda x: float(x)*0.74)
    df_sap_price['Active'] = 'A'
    for _, row in df_sap_matrix.iterrows():
        res_df = df_sap_price.copy()
        res_df['Wholesale Price'].apply(lambda x: float(x)*float(row['Discount']))
        res_df.to_excel(f'dist/SAP - PL{row["DiscountListNumber"]} - {row["Partner"]}.xlsx', index=False)

def _get_data(name):
    df_visa = blob.load_visa_file(name)
    # TODO save in db and retrieve later
    df_sap_matrix = pd.read_csv('sap_matrix.csv')
    return df_visa, df_sap_matrix

