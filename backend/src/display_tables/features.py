import pandas as pd
from src.database.db_operations import DBOperations
from src.utils.db_utils import filter_df_by_model_year

def query_features(country: str, model: str, model_year: int, engine: str, sales_version: str, gearbox: str):
# Prepare initial conditions for the PNO query
    conditions = [f"CountryCode = '{country}'"]
    if model:
        conditions.append(f"Model = '{model}'")
    if engine:
        conditions.append(f"Engine = '{engine}'")
    if sales_version:
        conditions.append(f"SalesVersion = '{sales_version}'")
    if gearbox:
        conditions.append(f"Gearbox = '{gearbox}'")

    # Query PNO data and filter by model year
    df_pnos = DBOperations.instance.get_table_df(
        DBOperations.instance.config.get('AUTH', 'PNO'),
        ['ID', 'Model', 'StartDate', 'EndDate'],
        conditions=conditions
    )
    df_pnos = filter_df_by_model_year(df_pnos, model_year)
    if df_pnos.empty:
        return []

    # Prepare conditions for the FEAT and CFEAT queries
    ids = df_pnos['ID'].tolist()
    pno_conditions = [f"PNOID = '{ids[0]}'"] if len(ids) == 1 else [f"PNOID in {tuple(ids)}"]

    # Query features and filter by model year
    df_features = DBOperations.instance.get_table_df(
        DBOperations.instance.config.get('TABLES', 'FEA'),
        columns=['Code', 'MarketText', 'StartDate', 'EndDate'],
        conditions=[f"CountryCode = '{country}'"]
    )
    df_features = filter_df_by_model_year(df_features, model_year)
    df_features = df_features.drop(columns=['StartDate', 'EndDate'])
    df_features['Code'] = df_features['Code'].str.strip()
    df_features = df_features.drop_duplicates(subset='Code')

    # Query PNO features and custom features
    df_pno_features = DBOperations.instance.get_table_df(
        DBOperations.instance.config.get('AUTH', 'FEAT'),
        columns=['PNOID', 'Code', 'CustomName', 'CustomCategory', 'Reference'],
        conditions=pno_conditions
    )
    df_pno_custom_features = DBOperations.instance.get_table_df(
        DBOperations.instance.config.get('AUTH', 'CFEAT'),
        columns=['PNOID', 'ID', 'Code', 'CustomName', 'CustomCategory'],
        conditions=pno_conditions
    )

    # Combine features and custom features
    df_pno_features = pd.concat([df_pno_features, df_pno_custom_features], ignore_index=True)
    df_pno_features['Code'] = df_pno_features['Code'].str.strip()
    df_pno_features['MarketText'] = df_pno_features['Code'].map(df_features.set_index('Code')['MarketText'])
    df_pno_features['ID'] = df_pno_features['ID'].fillna('')

    df_pno_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'OPT'), columns=['ID', 'PNOID', 'Code as OptCodeStr'], conditions=pno_conditions)
    df_pno_options = df_pno_options.drop_duplicates()
    # remove (u) from the end of the reference if exists otherwise replace with drop
    df_pno_options['OptCode'] = df_pno_options['OptCodeStr'].apply(lambda x: x.lstrip('0') if x.isnumeric() else x)

    df_pno_features_merged = df_pno_features.merge(df_pno_options[['PNOID', 'OptCode', 'OptCodeStr']], 
                                      how='left', 
                                      left_on=['PNOID', 'Reference'],
                                      right_on=['PNOID', 'OptCode'])
    df_pno_features_merged.drop(['OptCode'], axis=1)
    df_pno_features_merged['Code'] = df_pno_features_merged.apply(lambda row: row['Code'] + " (" + row['OptCodeStr'].strip() + ")" if pd.notnull(row['OptCodeStr']) else row['Code'], axis=1)

    # Create mappings
    pno_id_to_model = df_pnos.set_index('ID')['Model'].to_dict()
    custom_name_to_pnoid = df_pno_features_merged.groupby('CustomName')['PNOID'].apply(list).to_dict()

    # Aggregate data
    def aggregate_custom_name(custom_names):
        filtered_df = custom_names[custom_names.notnull() & (custom_names != "") & (custom_names != "Null")]
        
        # Strip and remove duplicates
        unique_names = filtered_df.unique()
        
        if len(unique_names) == 0:
            return ''
        elif len(unique_names) > 1:
            res_str = ''
            for name in unique_names:
                
                models = set()
                if name:
                    pno_ids = custom_name_to_pnoid.get(name, [])
                    for pno_id in pno_ids:
                        model = pno_id_to_model.get(pno_id, '')
                        if model:
                            models.add(model)
                if models:
                    res_str += f"({', '.join(sorted(models))}), "
                    
            return "Specific: " + res_str[:-2]
        return unique_names[0]
    
    df_pno_features_merged = df_pno_features_merged.groupby('Code').agg({
        'MarketText': 'first', 
        'CustomName': aggregate_custom_name,
        'CustomCategory': aggregate_custom_name, 
        'ID': lambda x: ','.join(x) if x.any() else ''
    }).reset_index()

    # Sort and remove duplicates
    df_pno_features_merged = df_pno_features_merged.sort_values(by='Code', ascending=True)
    df_pno_features_merged = df_pno_features_merged.drop_duplicates()
    
    return df_pno_features_merged