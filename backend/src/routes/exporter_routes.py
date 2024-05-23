import datetime
import io
import zipfile
from flask import Blueprint, request, send_file
import pandas as pd
from src.database.db_operations import DBOperations
from src.export.sap_price_list import get_sap_price_list
from src.export.variant_binder import extract_variant_binder
from src.storage.blob import load_available_visa_files
from src.utils.ingest_utils import is_valid_engine_category


bp_exporter = Blueprint('export', __name__, url_prefix='/api/<country>/export')

@bp_exporter.route('/variant_binder', methods=['GET'])
def variant_binder(country):
    time = request.args.get('date')
    model = request.args.get('model')
    engines_types = request.args.get('engines_category')
    
    if not time:
        return 'Time is required', 400
    elif len(time) != 6:
        return 'Invalid time format', 400
    
    if not model:
        return 'Model is required', 400
    
    if not engines_types and engines_types != '':
        return 'Engine category is required', 400
    elif not is_valid_engine_category(engines_types, time[:4], country, model):
        return 'Invalid engine category', 400
    
    try:
        xlsx_file, title = extract_variant_binder(country, model, engines_types, int(time))
    except Exception as e:
        return str(e), 500
    return send_file(xlsx_file, download_name=title, as_attachment=True), 200

@bp_exporter.route('/sap-price-list', methods=['POST'])
def sap_price_list(country):
    data = request.get_json()
    if not data:
        return 'Data is required', 400
    
    code = data.get('code', 'All')
    time = datetime.datetime.now().strftime("%Y%U")

    conditions = [f'CountryCode = {country}', f'StartDate <= {time}', f'EndDate >= {time}']
    if code != 'All':
        conditions.append(f'Code = {code}')
    df_channels = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'SC'), columns=['ID', 'Code', 'ChannelName'], conditions=conditions)
    if df_channels.empty:
        return 'Invalid code' if code != 'All' else f'No Sales Channel with the code {code} found', 400

    channel_ids = df_channels['ID'].tolist()
    discount_conditions = []
    if len (channel_ids) == 1:
        discount_conditions.append(f"ChannelID = '{channel_ids[0]}'")
    else:
        discount_conditions.append(f"ChannelID IN {tuple(channel_ids)}")
    df_discounts = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'DIS'), columns=['ID', 'ChannelID', 'DiscountPercentage', 'RetailPrice', 'WholesalePrice', 'ActiveStatus', 'AffectedVisaFile'], conditions=discount_conditions)
    
    discount_ids = df_discounts['ID'].tolist()
    local_option_conditions = []
    if len(discount_ids) == 1:
        local_option_conditions.append(f"DiscountID = '{discount_ids[0]}'")
    else:
        local_option_conditions.append(f"DiscountID IN {tuple(discount_ids)}")

    df_local_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'CLO'), columns=['FeatureCode', 'FeaturePrice', 'DiscountID'], conditions=local_option_conditions)
    
    available_visa_files = load_available_visa_files(country)

    df_discounts['AffectedVisaFile'] = df_discounts['AffectedVisaFile'].replace('All', ','.join(available_visa_files.keys()))
    df_discounts['AffectedVisaFile'] = df_discounts['AffectedVisaFile'].str.split(',')
    df_discounts = df_discounts.explode('AffectedVisaFile')
    df_discounts = df_discounts[df_discounts['AffectedVisaFile'].isin(available_visa_files.keys())]

    df_discounts = df_discounts.merge(df_channels, left_on='ChannelID', right_on='ID', suffixes=('_discount', '_channel'))
    df_discounts = df_discounts.drop(columns=['ID_channel', 'ChannelID'])
    df_discounts = df_discounts.rename(columns={'ID_discount': 'ID'})

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        for visa_file, df_discounts_group in df_discounts.groupby('AffectedVisaFile'):
            df_discount_options = df_local_options[df_local_options['DiscountID'].isin(df_discounts_group['ID'].tolist())]
            dfs = get_sap_price_list(available_visa_files[visa_file], df_discounts_group, df_discount_options)
            folder_name = visa_file
            for df in dfs:
                code, channel_name = df.name.split('+#+')
                excel_filename = f'SAP - PL{code} - {channel_name}.xlsx'
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                zip_file.writestr(f'{folder_name}/{excel_filename}', excel_buffer.getvalue())
            if len(dfs) > 1:
                concatenated_df = pd.concat(dfs)
                concat_excel_buffer = io.BytesIO()
                with pd.ExcelWriter(concat_excel_buffer, engine='openpyxl') as writer:
                    concatenated_df.to_excel(writer, index=False)
                zip_file.writestr(f'{folder_name}/MAWISTA ALL.xlsx', concat_excel_buffer.getvalue())


    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='sap_price_list.zip')
