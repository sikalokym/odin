import configparser
import pandas as pd
import zipfile
import io

from src.database.db_operations import DBOperations
from src.ingest.visa_files.services import get_available_visa_files
from src.utils.db_utils import format_float_string, get_column_map

def extract_sap_price_list(country, code, date, model_year):
    
    conditions = [f"CountryCode = '{country}'", f"ModelYear = '{model_year}'"]
    if date:
        conditions += [f"DateFrom <= '{date}'", f"DateTo >= '{date}'"]
    if code != 'All':
        conditions.append(f"Code = '{code}'")
    df_channels = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'SC'), columns=['ID', 'Code', 'ChannelName', 'DateFrom', 'DateTo'], conditions=conditions)
    if df_channels.empty:
        return 'Invalid code' if code != 'All' else f'No Sales Channel with the code {code} found', 400
    
    channel_ids = df_channels['ID'].tolist()
    rel_conditions = []
    if len(channel_ids) == 1:
        rel_conditions.append(f"ChannelID = '{channel_ids[0]}'")
    else:
        rel_conditions.append(f"ChannelID IN {tuple(channel_ids)}")
    df_discounts = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'DIS'), columns=['ID', 'ChannelID', 'DiscountPercentage', 'RetailPrice', 'WholesalePrice', 'PNOSpecific', 'AffectedVisaFile'], conditions=rel_conditions)
    
    if date:
        rel_conditions.append(f"DateFrom <= '{date}'")
        rel_conditions.append(f"DateTo >= '{date}'")
    
    df_local_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'CLO'), columns=['FeatureCode', 'FeatureRetailPrice', 'FeatureWholesalePrice', 'ChannelID', 'AffectedVisaFile', 'DateFrom', 'DateTo'], conditions=rel_conditions)
    
    visa_columns = ['VisaFile', 'CarType', 'ModelYear', 'DateFrom as StartDate']
    df_visa = get_available_visa_files(country, model_year, visa_columns)
    if df_visa.empty:
        return None
    df_visa = df_visa.drop_duplicates()
    
    # Group by 'VisaFile' and sort by 'DateFrom', then rank
    df_visa['Order'] = df_visa.sort_values(by=['ModelYear', 'CarType', 'StartDate']).groupby(['ModelYear', 'CarType']).cumcount() + 1
    df_visa = df_visa.drop(columns=['StartDate'])
    df_visa = df_visa.sort_values(by=['ModelYear', 'CarType', 'Order']).drop_duplicates(subset=['VisaFile', 'CarType', 'ModelYear'])
    
    available_visa_files = df_visa['VisaFile'].unique().tolist()
    def process_row(visa):
        if visa == 'All':
            return available_visa_files
        car_types = [name.split('[')[1].split(']')[0] for name in visa.split(',') if '[' in name and ']' in name]
        
        # Get visa files that have the same car type from df_visa
        return df_visa[df_visa['CarType'].isin(car_types)]['VisaFile'].tolist()
    
    df_local_options['VisaFile'] = df_local_options['AffectedVisaFile'].apply(process_row)
    df_local_options = df_local_options.explode('VisaFile')
    df_local_options = df_local_options[df_local_options['VisaFile'].isin(available_visa_files)]
    
    df_discounts['VisaFile'] = df_discounts['AffectedVisaFile'].apply(process_row)
    df_discounts = df_discounts.explode('VisaFile')
    df_discounts = df_discounts[df_discounts['VisaFile'].isin(available_visa_files)]
    
    df_discounts = df_discounts.merge(df_visa[['VisaFile', 'Order']], left_on='VisaFile', right_on='VisaFile', suffixes=('_discount', '_visa'))
    
    df_discounts = df_discounts.merge(df_channels, left_on='ChannelID', right_on='ID', suffixes=('_discount', '_channel'))
    df_discounts = df_discounts.drop(columns=['ID_channel', 'ID_discount'])
    df_discounts = df_discounts.rename(columns={'ChannelID': 'ID'})
    
    today = pd.Timestamp.now().strftime('%Y.%m.%d')
    today = today[2:].replace('.', '')
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        for visa_file, df_discounts_group in df_discounts.groupby('VisaFile'):
            df_discount_options = df_local_options[(df_local_options['ChannelID'].isin(df_discounts_group['ID'].tolist())) & (df_local_options['VisaFile'] == visa_file)]
            dfs = get_sap_price_list(visa_file, df_discounts_group, df_discount_options, model_year, country)
            car_type = df_visa[df_visa['VisaFile'] == visa_file]['CarType'].iloc[0]
            folder_name = visa_file
            used_names = []
            # sort dfs after code
            dfs = sorted(dfs, key=lambda x: x.name.split('+#+')[0])
            for df in dfs:
                code, channel_name = df.name.split('+#+')
                excel_filename = f'{today} SAP - PL{code} - {channel_name} - {car_type}.xlsx'
                suffix = 1
                while excel_filename in used_names:
                    excel_filename = f'{today} SAP - PL{code} - {channel_name} - {car_type} ({suffix}).xlsx'
                    suffix += 1
                used_names.append(excel_filename)
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                zip_file.writestr(f'{folder_name}/{excel_filename}', excel_buffer.getvalue())
            if len(dfs) > 1:
                concatenated_df = pd.concat(dfs)
                concat_excel_buffer = io.BytesIO()
                with pd.ExcelWriter(concat_excel_buffer, engine='openpyxl') as writer:
                    concatenated_df.to_excel(writer, index=False)
                zip_file.writestr(f'{folder_name}/MASTA ALL.xlsx', concat_excel_buffer.getvalue())

    zip_buffer.seek(0)
    return zip_buffer

def get_sap_price_list(visa_file, df_sales_channels, df_discount_options, model_year, country_code):
    config = configparser.ConfigParser()
    config.read(f'config/sap_price_list/{country_code}.cfg')
    df_visa = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), conditions=[f"CountryCode = '{country_code}'", f"VisaFile = '{visa_file}'", f"ModelYear = '{model_year}'"])
    df_visa = df_visa.drop(columns=['CountryCode', 'VisaFile', 'ID', 'LoadingDate'])
    c_map = get_column_map(reverse=True)
    df_visa.columns = [c_map.get(col, col) for col in df_visa.columns]
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
    df_sap_price['Transfer Price'] = df_sap_price['Retail Price'].apply(lambda x: float(x) * transfer_price_factor)
    df_sap_price['Active'] = config['DEFAULT']['ACTIVE']
    dfs = []
    
    for _, row in df_sales_channels.iterrows():
        res_df = df_sap_price.copy()
        if row['DiscountPercentage'] is not None:
            res_df['Wholesale Price'] = res_df['Retail Price'].apply(lambda x: float(x)* (1-float(row['DiscountPercentage'])*0.01))
        else:
            res_df['Wholesale Price'] = row['WholesalePrice']
            res_df['Retail Price'] = row['RetailPrice']
        if row['PNOSpecific']:
            res_df = prepare_pno_specific_discount(res_df)
        res_df['Price List'] = row['Code']
        
        if row['Order'] == 1:
            res_df['Date From'] = pd.to_datetime(row['DateFrom'])
            res_df['Date From'] = res_df['Date From'].dt.strftime('%Y.%m.%d')
        
        res_df['Date To'] = pd.to_datetime(row['DateTo'])
        res_df['Date To'] = res_df['Date To'].dt.strftime('%Y.%m.%d')

        df_local_options = df_discount_options[df_discount_options['ChannelID'] == row['ID']]
        res_df = add_local_codes(res_df, df_local_options)
        res_df['Wholesale Price'] = res_df['Wholesale Price'].apply(format_float_string)
        res_df['Retail Price'] = res_df['Retail Price'].apply(format_float_string)
        res_df['Transfer Price'] = res_df['Transfer Price'].apply(format_float_string)
        
        # Fill na values with empty strings
        res_df = res_df.fillna('')
        
        # Create sorting key columns
        res_df['is_empty_all'] = (res_df[['Color', 'Option', 'Upholstery', 'Package']] == '').all(axis=1).astype(int)
        res_df['is_not_empty_option'] = (res_df['Option'] != '').astype(int)
        res_df['is_not_empty_package'] = (res_df['Package'] != '').astype(int)
        res_df['is_not_empty_upholstery'] = (res_df['Upholstery'] != '').astype(int)
        res_df['is_not_empty_color'] = (res_df['Color'] != '').astype(int)

        # Sort the DataFrame
        res_df = res_df.sort_values(
            by=['is_empty_all', 'is_not_empty_option', 'is_not_empty_package', 'is_not_empty_upholstery', 'is_not_empty_color'],
            ascending=[False, False, False, False, False]
        ).drop(columns=['is_empty_all', 'is_not_empty_option', 'is_not_empty_package', 'is_not_empty_upholstery', 'is_not_empty_color'])

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
        try:
            new_row = last_row.copy()
            new_row['Option'] = row['FeatureCode']
            new_row['Wholesale Price'] = row['FeatureWholesalePrice']
            new_row['Retail Price'] = row['FeatureRetailPrice']
            row['Date From'] = pd.to_datetime(row['DateFrom'])
            new_row['Date From'] = row['Date From'].strftime('%Y.%m.%d')
            row['Date To'] = pd.to_datetime(row['DateTo'])
            new_row['Date To'] = row['Date To'].strftime('%Y.%m.%d')
        except Exception as e:
            DBOperations.instance.logger.error(f'Error processing local codes: {e}', extra={'country_code': 'All'})
            continue
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df

def prepare_pno_specific_discount(df):
    df = df.fillna('')
    mask_all_empty = df[['Color', 'Option', 'Upholstery', 'Package']] == ''
    mask_all_empty = mask_all_empty.all(axis=1)
    
    # Separate the dataframe into two parts
    df_pno_prices = df[mask_all_empty]
    df_pno_non_prices = df[~mask_all_empty]
    
    # Set prices to 0 for the non-price-specific rows
    df_pno_non_prices[['Retail Price', 'Wholesale Price', 'Transfer Price']] = 0
    
    # Concatenate the two dataframes and return the result
    return pd.concat([df_pno_prices, df_pno_non_prices], ignore_index=True)
