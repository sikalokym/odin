from flask import Blueprint, request, send_file
import pandas as pd
import zipfile
import io
import os

from src.export.variant_binder import extract_variant_binder, extract_variant_binder_pnos
from src.export.sap_price_list import extract_sap_price_list
from src.utils.ingest_utils import is_valid_engine_category
from src.database.db_operations import DBOperations
from src.utils.db_utils import get_column_map
from src.export.database import features

# @author Hassan Wahba

bp_exporter = Blueprint('export', __name__, url_prefix='/api/<country>/export')

@bp_exporter.route('/features', methods=['GET'])
def download_features(country):
    model = request.args.get('model')
    engine = request.args.get('engine')
    sales_version = request.args.get('sales_version')
    gearbox = request.args.get('gearbox')
    model_year = request.args.get('model_year')

    output = features.extract_features(country=country,
                                       model=model,
                                       model_year=model_year,
                                       engine=engine,
                                       sales_version=sales_version,
                                       gearbox=gearbox)
    return send_file(output, download_name="Features.xlsx", as_attachment=True), 200    
    

@bp_exporter.route('/variant_binder/pnos', methods=['GET'])
def variant_binder_pnos(country):
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
        df_pnos = extract_variant_binder_pnos(country, model, engines_types, int(time))
        return df_pnos.to_json(orient='records'), 200
    except Exception as e:
        return str(e), 500

@bp_exporter.route('/variant_binder', methods=['GET'])
def variant_binder(country):
    model = request.args.get('model')
    engines_types = request.args.get('engines_category')
    time = request.args.get('date')
    pnos = request.args.get('pnos', None)
    if pnos:
        pnos = pnos.split(',')
    sv_order = request.args.get('sv_order', None)
    if sv_order:
        sv_order = sv_order.split(',')
    
    try:
        xlsx_file, title = extract_variant_binder(country, model, engines_types, int(time), pnos, sv_order)
    except Exception as e:
        return str(e), 500
    return send_file(xlsx_file, download_name=title, as_attachment=True), 200

@bp_exporter.route('/sap-price-list', methods=['GET'])
def sap_price_list(country):
    code = request.args.get('code', 'All')
    date = request.args.get('date', '')
    model_year = request.args.get('model_year', '')
    if not model_year:
        return 'Model year is required', 400
    
    today = pd.Timestamp.now().strftime('%Y.%m.%d')
    today = today[2:].replace('.', '')
    download_name = f'{today} SAP Price Lists.zip'
    
    zip_buffer = extract_sap_price_list(country, code, date, model_year)
    if not zip_buffer:
        return 'No data found', 404
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=download_name)

@bp_exporter.route('/visa', methods=['GET'])
def export_visa_file(country):
    visa_file_name = request.args.get('VisaFile')
    if not visa_file_name:
        return "VisaFile is required", 400
    try:
        table_name = DBOperations.instance.config.get('RELATIONS', 'RAW_VISA')
        df_visa = DBOperations.instance.get_table_df(table_name, conditions=[f"CountryCode = '{country}'", f"VisaFile = '{visa_file_name}'"])
        if df_visa.empty:
            return "Visa file not found", 404
        df_visa = df_visa.drop(columns=['CountryCode', 'VisaFile', 'ID', 'LoadingDate'])
        c_map = get_column_map(reverse=True)
        df_visa.columns = [c_map.get(col, col) for col in df_visa.columns]

        # Create sorting key columns
        df_visa['is_empty_all'] = (df_visa[['Color', 'Option', 'Upholstery', 'Package']] == '').all(axis=1).astype(int)
        df_visa['is_not_empty_option'] = (df_visa['Option'] != '').astype(int)
        df_visa['is_not_empty_package'] = (df_visa['Package'] != '').astype(int)
        df_visa['is_not_empty_upholstery'] = (df_visa['Upholstery'] != '').astype(int)
        df_visa['is_not_empty_color'] = (df_visa['Color'] != '').astype(int)

        # Sort the DataFrame
        df_sorted = df_visa.sort_values(
            by=['is_empty_all', 'is_not_empty_option', 'is_not_empty_package', 'is_not_empty_upholstery', 'is_not_empty_color'],
            ascending=[False, False, False, False, False]
        ).drop(columns=['is_empty_all', 'is_not_empty_option', 'is_not_empty_package', 'is_not_empty_upholstery', 'is_not_empty_color'])

        # Create a buffer to hold the Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_sorted.to_excel(writer, index=False)

        output.seek(0)
        download_name = visa_file_name if visa_file_name.endswith('.xlsx') else f'{visa_file_name}.xlsx'
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=download_name)
    except Exception as e:
        return str(e), 500

@bp_exporter.route('/technical-logs', methods=['GET'])
def export_logs(country):
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        return "Log directory not found", 404
    
    # Create a BytesIO object to hold the zip file in memory
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for root, _, files in os.walk(log_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zf.write(file_path, os.path.relpath(file_path, log_dir))
    
    memory_file.seek(0)
    
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='logs.zip')