import pandas as pd
import configparser
from src.storage import blob
from src.database.db_operations import DBOperations
from src.utils.db_utils import split_df

config = configparser.ConfigParser()
config.read('config/sap_price_list.cfg')

def get_sap_price_list(name, df_sales_channels, df_discount_options):
    df_visa = blob.load_visa_file(name)

    columns_to_drop = config['DEFAULT']['COLUMNS_TO_DROP'].split(',')
    df_sap_price = df_visa.drop(columns=columns_to_drop)
    df_sap_price = df_sap_price.rename(columns={'Price Before Tax': 'Retail Price'})
    df_sap_price['Date From'] = pd.to_datetime(df_sap_price['Date From'])
    df_sap_price['Date To'] = pd.to_datetime(df_sap_price['Date To'])

    date_format = config['DEFAULT']['DATE_FORMAT']
    df_sap_price['Date From'] = df_sap_price['Date From'].dt.strftime(date_format)
    df_sap_price['Date To'] = df_sap_price['Date To'].dt.strftime(date_format)

    df_sap_price['Sales Org.'] = config['DEFAULT']['SALES_ORG']
    df_sap_price['Structure week'] = config['DEFAULT']['STRUCTURE_WEEK']
    transfer_price_factor = float(config['DEFAULT']['TRANSFER_PRICE_FACTOR'])
    df_sap_price['Transfer Price'].apply(lambda x: float(x)*transfer_price_factor)
    df_sap_price['Active'] = config['DEFAULT']['ACTIVE']
    dfs = []
    for _, row in df_sales_channels.iterrows():
        res_df = prepare_pno_specific_discount(df_sap_price.copy()) if row['PNOSpecific'] else df_sap_price.copy()
        res_df['Wholesale Price'] = res_df['Wholesale Price'].apply(lambda x: float(x)* (1-float(row['DiscountPercentage'])*0.01))
        res_df['Price List'] = row['Code']
        df_local_options = df_discount_options[df_discount_options['ChannelID'] == row['ID']]
        res_df = add_local_codes(res_df, df_local_options)
        res_df.name = f"{row['Code']}+#+{row['ChannelName']}"
        dfs.append(res_df)

    return dfs

def add_local_codes(df, df_codes):
    last_row = df.iloc[-1].copy()
    last_row['Sales Version'] = '-'
    last_row['Market Code'] = '-'
    last_row['Engine'] = '-'
    last_row['Body'] = '-'
    last_row['Steering'] = '-'
    last_row['Transfer Price'] = 0
    last_row['Color'] = None
    last_row['Upholstery'] = None
    last_row['Package'] = None
    for _, row in df_codes.iterrows():
        new_row = last_row.copy()
        new_row['Option'] = row['FeatureCode']
        new_row['Wholesale Price'] = row['FeatureWholesalePrice']
        new_row['Retail Price'] = row['FeatureRetailPrice']
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df

def prepare_pno_specific_discount(df):
    # Identify rows with all specified columns as null
    mask_all_null = df[['Color', 'Option', 'Upholstery', 'Package']].isnull().all(axis=1)
    
    # Separate the dataframe into two parts
    df_pno_prices = df[mask_all_null]
    df_pno_non_prices = df[~mask_all_null]
    
    # Set prices to 0 for the non-price-specific rows
    df_pno_non_prices[['Retail Price', 'Wholesale Price', 'Transfer Price']] = 0
    
    # Concatenate the two dataframes and return the result
    return pd.concat([df_pno_prices, df_pno_non_prices], ignore_index=True)

