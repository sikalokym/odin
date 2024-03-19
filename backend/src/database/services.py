from src.database.db_operations import DBOperations
from src.utils.db_utils import get_model_year_from_date


def get_engine_cats(country, model_year, model):
    conditions = [f'CountryCode = {country}']
    
    if model:
        conditions.append(f'Model = {model}')

    pno_engins = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'PNO'), columns=['Engine', 'StartDate'], conditions=conditions)
    pno_engins['ModelYear'] = pno_engins['StartDate'].apply(get_model_year_from_date)
    pno_engins = pno_engins[pno_engins['ModelYear'] == int(model_year)]

    engines = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'En'), columns=['Code', 'EngineCategory'], conditions=[f'CountryCode = {country}'])
    engines = engines[engines['Code'].isin(pno_engins['Engine'])]
    engines = engines.dropna(subset=['EngineCategory'])
    engine_cats = engines['EngineCategory'].unique().tolist()
    return engine_cats