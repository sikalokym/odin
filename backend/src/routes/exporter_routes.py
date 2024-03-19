from flask import Blueprint, request, send_file
from src.export.variant_binder import extract_variant_binder
from src.utils.ingest_utils import is_valid_car_type, is_valid_engine_category


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
    elif not is_valid_car_type(model, time[:4], country):
        return 'Invalid car type', 400
    
    if not engines_types and engines_types != '':
        return 'Engine category is required', 400
    elif not is_valid_engine_category(engines_types, time[:4], country, model):
        return 'Invalid engine category', 400
    
    
    xlsx_file = extract_variant_binder(country, model, engines_types, int(time))
    return send_file(xlsx_file, download_name=f'VB {model} - {time} {engines_types}.xlsx', as_attachment=True), 200
