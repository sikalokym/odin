from cachetools import cached, TTLCache
from contextlib import contextmanager
import configparser
import pandas as pd
import logging
import time

from src.database.db_connection import DatabaseConnection
import src.utils.db_utils as utils


class DBOperations:
    instance = None
    cache = TTLCache(maxsize=100, ttl=60000)

    @classmethod
    def create_instance(cls, logger=None, test=False):
        config = configparser.ConfigParser()
        config.read('config/data_model.cfg')
        conn = DatabaseConnection.get_db_connection(test=test)
        cls.instance = cls(conn, config, logger)
        return cls.instance
    
    def __init__(self, db_conn, config, logger=None):
        self.conn = db_conn
        self.config = config
        self.logger = logger or logging.getLogger(__name__)

    @contextmanager
    def get_cursor(self):
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.logger.error(f'Database operation failed: {e}', exc_info=True)
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def get_table_df(self, table_name, columns=None, conditions=None):
        if columns is None:
            columns = '*'
        elif isinstance(columns, list):
            columns = ', '.join(columns)
        elif isinstance(columns, str):
            if columns != '*' and not columns.replace(' ', '').replace(',', '').isalpha():
                raise ValueError('Invalid column format')
        else:
            raise ValueError('Columns must be a list')
        
        if conditions is None or conditions == '':
            conditions = '1=1'
        elif isinstance(conditions, list):
            if conditions == []:
                conditions = '1=1'
            conditions = ' AND '.join(conditions)
        else:
            raise ValueError('Conditions must be a list')
        
        return self.get_table_df_cached(table_name, columns, conditions)
        
    @cached(cache)
    def _get_table_df_cached(self, table_name, columns, conditions):
        
        with self.get_cursor() as cursor:
            cursor.execute(f"SELECT {columns} FROM {table_name} WHERE {conditions};")
            data = cursor.fetchall()
            if not data:
                columns = [column.strip() for column in columns.split(',')]
                if columns == ['*']:
                    return pd.DataFrame([])
                return pd.DataFrame([], columns=columns)
            columns = [column[0] for column in data[0].cursor_description]
            data = [list(row) for row in data]
            df = pd.DataFrame(data, columns=columns)
            return df
        
    @cached(cache)
    def get_table_df_cached(self, table_name, columns, conditions):
        attempts = 3  # Define the number of retry attempts
        while attempts > 0:
            try:
                with self.get_cursor() as cursor:
                    cursor.execute(f"SELECT {columns} FROM {table_name} WHERE {conditions};")
                    data = cursor.fetchall()
                    if not data:
                        columns_list = [column.strip() for column in columns.split(',')]
                        return pd.DataFrame([], columns=columns_list if columns_list != ['*'] else [])
                    df_columns = [column[0] for column in data[0].cursor_description]
                    df_data = [list(row) for row in data]
                    return pd.DataFrame(df_data, columns=df_columns)
            except Exception as e:
                self.logger.error(f'Attempt failed with error: {e}', exc_info=True)
                self.logger.error(f'Query: SELECT {columns} FROM {table_name} WHERE {conditions};')
                attempts -= 1
                if attempts > 0:
                    self.conn = DatabaseConnection.reconnect()
                    self.logger.info(f'Retrying... {attempts} attempts left')
                    time.sleep(2)
                else:
                    self.logger.error('All attempts to execute the query have failed.')
                    raise

    def upsert_data_from_df(self, df, table_name, columns, conditional_columns):
        if df.empty:
            self.logger.warning('No data to insert')
            return
        self.create_temp_staging_table(table_name, columns)
        self.insert_data_into_staging(table_name, df, columns, conditional_columns)
        self.merge_data_from_staging(table_name, columns, conditional_columns)
        self.drop_temp_staging_table(table_name)
        self.cache.clear()
    
    def create_temp_staging_table(self, target_table_name, cols):
        try:
            with self.get_cursor() as cursor:
                # Check if the temporary staging table exists and delete it if it does
                cursor.execute(f"""
                    IF OBJECT_ID('tempdb..#tmp_staging_{target_table_name}') IS NOT NULL
                    DROP TABLE #tmp_staging_{target_table_name};
                """)

                # Create the new temporary staging table
                cursor.execute(f"""
                    SELECT {', '.join(cols)} 
                    INTO #tmp_staging_{target_table_name}
                    FROM {target_table_name}
                    WHERE 1=0;
                """)
        except Exception as e:
            self.logger.error(f"Error creating temporary staging table: {e}")
            raise e

    def insert_data_into_staging(self, target_table_name, df, columns, conditional_columns):
        # Ensure the DataFrame is not empty
        if df.empty:
            self.logger.error("The DataFrame is empty. No data to insert.")
            return
        
        # Check columns exist in the DataFrame
        try:
            df = df[columns]
        except KeyError as e:
            self.logger.error(f"Error inserting data into temporary staging table: {e}")
            raise e

        df = df.drop_duplicates(subset=conditional_columns)

        with self.get_cursor() as cursor:
            try:
                # Enable fast_executemany for improved performance
                cursor.fast_executemany = True

                # Convert the list of columns into a comma-separated string
                columns_str = ', '.join(columns)

                # Create placeholders for each column
                placeholders = ', '.join(['?'] * len(columns))

                # Generate the SQL command
                sql = f"""
                INSERT INTO #tmp_staging_{target_table_name}({columns_str})
                VALUES ({placeholders})
                """

                # Convert the DataFrame to a list of tuples
                params = list(df.itertuples(index=False, name=None))

                # Execute the query using executemany
                cursor.executemany(sql, params)
                
            except Exception as e:
                self.logger.error(f"Failed to insert data with fast_executemany: {e}")
                # try again without fast_executemany
                cursor.fast_executemany = False
                try:
                    cursor.executemany(sql, params)
                except Exception as e:
                    self.logger.error(f"Error inserting data into temporary staging table: {e}")
                    raise e

    def merge_data_from_staging(self, target_table_name, all_columns, conditional_columns):
        try:
            with self.get_cursor() as cursor:

                # Remove the conditional columns from the list of columns to update
                upsert_columns = [col for col in all_columns if col not in conditional_columns]

                update_sql = ', '.join([f"TARGET.{col} = SOURCE.{col}" for col in upsert_columns])
                conditional_columns_sql = ' AND '.join([f"TARGET.{col} = SOURCE.{col}" for col in conditional_columns])

                # Construct the SQL for the INSERT part of the MERGE
                insert_columns_sql = ', '.join(all_columns)
                insert_values_sql = ', '.join([f"SOURCE.{col}" for col in all_columns])

                # Full MERGE SQL command
                sql_command = f"""
                    MERGE INTO {target_table_name} AS TARGET
                    USING #tmp_staging_{target_table_name} AS SOURCE
                    ON {conditional_columns_sql}
                """
                
                if update_sql:
                    sql_command += f"""
                    WHEN MATCHED THEN
                        UPDATE SET {update_sql}
                    """
                    
                sql_command += f"""
                    WHEN NOT MATCHED BY TARGET THEN
                        INSERT ({insert_columns_sql})
                        VALUES ({insert_values_sql});
                """
                
                cursor.execute(sql_command)
        except Exception as e:
            self.logger.error(f"Error merging data from temporary staging table: {e}")
            raise e

    def drop_temp_staging_table(self, target_table_name):
        try:
            with self.get_cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS #tmp_staging_{target_table_name};")
        except Exception as e:
            self.logger.error(f"Error dropping temporary staging table: {e}")

    def collect_entity(self, df, country_code):
        df['DataType'] = df['DataType'].fillna('')
        df['DataType'] = df.apply(lambda row: row['MainDataType'] if row['DataType'] == '' else row['DataType'], axis=1)
        df = df.drop('MainDataType', axis=1)
        df.insert(5, 'CountryCode', country_code)

        self.logger.debug('Inserting entities')
        entities_with_translation = ['Typ', 'SV', 'G']
        for data_type, group in df.groupby('DataType'):
            entity_columns = ['Code', 'Special', 'ShortText', 'MarketText', 'CountryCode', 'StartDate', 'EndDate']
            if data_type in entities_with_translation:
                for code in group['Code'].unique():
                    old_df = DBOperations.instance.get_table_df(self.config.get('TABLES', data_type), conditions=[f"CountryCode='{country_code}'", f"Code='{code}'"])
                    if not old_df.empty:
                        custom_names = old_df['CustomName'].unique().tolist()
                        custom_names = [name for name in custom_names if name]
                        if len(custom_names) > 1:
                            self.logger.warning(f"Multiple custom names found for code {code} in {data_type}")
                        elif len(custom_names) == 0:
                            self.logger.warning(f"No custom name found for code {code} in {data_type}") 
                        else:
                            group.loc[group['Code'] == code, 'CustomName'] = custom_names[0]
                entity_columns.insert(-3, 'CustomName')
            elif data_type == 'En':
                for code in group['Code'].unique():
                    old_df = DBOperations.instance.get_table_df(self.config.get('TABLES', data_type), conditions=[f"CountryCode='{country_code}'", f"Code='{code}'"])
                    if not old_df.empty:
                        old_df = old_df.dropna(subset=['CustomName'])
                        if old_df.empty:
                            self.logger.warning(f"No custom name found for code {code} in {data_type}")
                        else:
                            group.loc[group['Code'] == code, 'CustomName'] = old_df['CustomName'].values[0]
                            group.loc[group['Code'] == code, 'Performance'] = old_df['Performance'].values[0]
                            group.loc[group['Code'] == code, 'EngineCategory'] = old_df['EngineCategory'].values[0]
                            group.loc[group['Code'] == code, 'EngineType'] = old_df['EngineType'].values[0]
                            if 'CustomName' not in entity_columns:
                                entity_columns.insert(-3, 'CustomName')
                                entity_columns.insert(-3, 'Performance')
                                entity_columns.insert(-3, 'EngineCategory')
                                entity_columns.insert(-3, 'EngineType')
            
            table_name = self.config.get('TABLES', data_type)
            conditional_columns = ['Code', 'Special', 'CountryCode', 'StartDate']
            group = group.drop('DataType', axis=1).reindex(columns=entity_columns)
            
            # Fill the missing columns with empty strings
            group = group.fillna('')
            self.upsert_data_from_df(group, table_name, entity_columns, conditional_columns)

    def drop_entity(self, df, country_code):
        df['DataType'] = df.apply(lambda row: row['MainDataType'] if row['DataType'] == '' else row['DataType'], axis=1)
        df = df.drop('MainDataType', axis=1)

        for data_type, group in df.groupby('DataType'):
            table_name = self.config.get('TABLES', data_type)
            group = group[['Code','StartDate']]
            self.delete_matching_entries(group, table_name, country_code)

    def delete_matching_entries(self, df, table_name, country_code):
        # Group by 'StartDate' and aggregate 'Code' into lists
        aggregated = df.groupby('StartDate').agg({'Code': lambda x: list(x)}).reset_index()

        # Iterate through each group to form conditions
        or_conditions = []
        for _, row in aggregated.iterrows():
            codes = row['Code']
            start_date = row['StartDate']
            
            # Check if codes list has only one element or more
            if len(codes) == 1:
                condition = f"(Code = {codes[0]} AND StartDate = {start_date})"
            else:
                codes_str = tuple(codes)
                condition = f"(Code IN {codes_str} AND StartDate = {start_date})"
            
            or_conditions.append(condition)

        or_conditions_str = ' OR '.join(or_conditions)
        conditions = [f"CountryCode = '{country_code}'", or_conditions_str]
        conditions_str = ' AND '.join(conditions)
        
        delete_query = f"DELETE FROM {table_name} WHERE {conditions_str};"

        # Execute the delete query using the context manager
        with self.get_cursor() as cursor:
            cursor.execute(delete_query)
            self.logger.info(f"Deleted {cursor.rowcount} entries from {table_name}")

    def collect_auth(self, df, country_code):
        df_pno = df[df['DataType'] == 'PNO'].copy()
        df_pno.insert(9, 'CountryCode', country_code)
        df = df[df['DataType'] != 'PNO'].copy()

        self.logger.debug('Inserting PNOs')
        pno_columns = ['Code', 'Model', 'Engine', 'SalesVersion', 'Steering', 'Gearbox', 'Body', 'MarketCode', 'CountryCode', 'StartDate', 'EndDate']
        conditional_columns = ['Code', 'CountryCode', 'StartDate']
        df_pno = df_pno.drop(['RuleName', 'DataType'], axis=1)
        
        # if not df_pno.empty:
            # self.upsert_data_from_df(df_pno, self.config.get('AUTH', 'PNO'), pno_columns, conditional_columns)
        df_pno['Condition'] = df_pno.apply(lambda row: f"Code = '{row['Code']}' AND CountryCode = '{row['CountryCode']}' AND StartDate = {row['StartDate']}", axis=1)
        conditions = [' OR '.join(df_pno['Condition'].tolist())]
        
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=conditions)
        return df_pnos
    
        if df_pnos.empty:
            self.logger.warning("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        
        df_assigned, df_unassigned = utils.get_pno_ids_from_variants(df_pnos, df)
        for data_type, group in df_assigned.groupby('DataType'):
            group = group.drop('DataType', axis=1)
            utils.log_df(df_unassigned, f'{data_type} from CPAM were not assigned to any existing authorized PNOs. Should have been removed as it was deauthorized::', self.logger.error)
        
        auth_columns = ['PNOID', 'Code', 'RuleName', 'StartDate', 'EndDate']
        auth_conditional_columns = ['PNOID', 'Code', 'StartDate']
        self.logger.debug('Inserting authorizations')
        for data_type, group in df_assigned.groupby('DataType'):
            group = group.drop('DataType', axis=1)
            self.upsert_data_from_df(group, self.config.get('AUTH', data_type), auth_columns, auth_conditional_columns)
            pno_ids = group['PNOID'].unique().tolist()
            
            conditions = []
            if len(pno_ids) == 1:
                conditions.append(f"PNOID = '{pno_ids[0]}'")
            else:
                conditions.append(f"PNOID in {tuple(pno_ids)}")
            df_inserted = self.get_table_df(self.config.get('AUTH', data_type), columns=['ID as RelationID', 'Code', 'StartDate', 'EndDate'], conditions=conditions)
            ids = df_inserted['RelationID'].unique().tolist()
            conditions = []
            if len(ids) == 1:
                conditions.append(f"RelationID = '{ids[0]}'")
            else:
                conditions.append(f"RelationID in {tuple(ids)}")
            df_relation = self.get_table_df(self.config.get('RELATIONS', f'{data_type}_Custom'), conditions=conditions)
            if df_relation.empty:
                df_inserted['CustomName'] = ''
                self.upsert_data_from_df(df_inserted, self.config.get('RELATIONS', f'{data_type}_Custom'), ['RelationID', 'CustomName', 'StartDate', 'EndDate'], ['RelationID'])
                continue
            df_relation = df_relation.drop(['StartDate', 'EndDate'], axis=1)
            df_inserted = df_inserted.merge(df_relation, on=['RelationID'], how='left')
            
            df_inserted['CustomName'] = df_inserted.groupby('Code').apply(utils.fill_custom_name).reset_index(drop=True)
            self.upsert_data_from_df(df_inserted, self.config.get('RELATIONS', f'{data_type}_Custom'), ['RelationID', 'CustomName', 'StartDate', 'EndDate'], ['RelationID'])
        
        return df_pnos

    def delete_ids_from_table(self, table_name, ids, id_column):
        if not ids:
            self.logger.info('No IDs to delete')
            return
        condition = ''
        if len(ids) == 1:
            condition = f"{id_column} = '{ids[0]}'"
        else:
            condition = f"{id_column} IN {tuple(ids)}"
            
        with self.get_cursor() as cursor:
            cursor.execute(f"DELETE FROM {table_name} WHERE {condition};")
            self.logger.info(f"Deleted {cursor.rowcount} entries from {table_name}")

    def set_enddate(self, table_name, ids, id_column):
        if not ids:
            self.logger.info('No IDs to delete')
            return
        condition = ''
        if len(ids) == 1:
            condition = f"{id_column} = '{ids[0]}'"
        else:
            condition = f"{id_column} IN {tuple(ids)}"
        
        df = self.get_table_df(table_name, columns=[id_column, 'EndDate'], conditions=[condition])
        end_date = utils.get_last_week_date()
        
        def decide_end_date(end_date_value):
            # Logic must be discussed with the product team
            if isinstance(end_date_value, int):
                curr_year = utils.get_model_year_from_date(end_date)
                year = utils.get_model_year_from_date(end_date_value)
                if curr_year != year:
                    return end_date_value
                return min(end_date_value, end_date)
            return end_date
        
        df['EndDate'] = df['EndDate'].map(decide_end_date)
        
        self.upsert_data_from_df(df, table_name, [id_column, 'EndDate'], [id_column])

    def drop_auth(self, df_unauth, country_code):
        self.logger.debug('deleting PNOs')
        model = df_unauth.iloc[0]['Model']
        start_dates = df_unauth['StartDate'].unique().tolist()
        conditions = [f"CountryCode='{country_code}'", f"Model='{model}'"]
        if len(start_dates) == 1:
            conditions.append(f"StartDate={start_dates[0]}")
        else:
            conditions.append(f"StartDate IN {tuple(start_dates)}")
        
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=conditions)
        
        if df_pnos.empty:
            self.logger.warning("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        
        df, _ = utils.get_pno_ids_from_variants(df_pnos, df_unauth)
        if df.empty:
            self.logger.info('No authorizations to delete')
            return
        
        df_non_pno = df[df['DataType'] != 'PNO']
        if not df_non_pno.empty:
            for data_type, group in df_non_pno.groupby('DataType'):
                group = group.drop('DataType', axis=1)
                filter_func = lambda row: f"PNOID = '{row['PNOID']}' AND Code = '{row['Code']}' AND RuleName = '{row['RuleName']}'" if group.shape[0] == 1 else f"(PNOID = '{row['PNOID']}' AND Code = '{row['Code']}' AND RuleName = '{row['RuleName']}')"
                
                group['Condition'] = group.apply(filter_func, axis=1)
                conditions = [' OR '.join(group['Condition'].tolist())]
                conditions = group['Condition'].tolist()
                all_ids = []
                chunk_size = 100
                for i in range(0, len(conditions), chunk_size):
                    chunk = conditions[i:i+chunk_size]
                    or_conditions = [' OR '.join(chunk)]
                    df_inserted = self.get_table_df(self.config.get('AUTH', data_type), columns=['ID'], conditions=or_conditions)
                    ids = df_inserted['ID'].unique().tolist()
                    if ids:
                        all_ids.extend(ids)
                if all_ids:
                    self.delete_ids_from_table(self.config.get('RELATIONS', f'{data_type}_Custom'), ids, 'RelationID')
                    self.delete_ids_from_table(self.config.get('AUTH', data_type), ids, 'ID')
        
        df_pno = df[df['DataType'] == 'PNO']
        pnoids = df_pno['PNOID'].unique().tolist()
        if not pnoids:
            return
        conds = [f"PNOID = '{pnoids[0]}'"] if len(pnoids) == 1 else [f"PNOID IN {tuple(pnoids)}"]
        
        self.delete_ids_from_table(self.config.get('AUTH', 'FEAT'), pnoids, 'PNOID')
        self.delete_ids_from_table(self.config.get('AUTH', 'CFEAT'), pnoids, 'PNOID')
        related_tables = ['COL', 'OPT', 'UPH', 'PKG']
        for table in related_tables:
            tmp_df = self.get_table_df(self.config.get('AUTH', table), ['ID'], conditions=conds)
            if tmp_df.empty:
                continue
            rel_ids = tmp_df['ID'].unique().tolist()
            self.delete_ids_from_table(self.config.get('RELATIONS', f'{table}_Custom'), rel_ids, 'RelationID')
            self.delete_ids_from_table(self.config.get('AUTH', table), rel_ids, 'ID')
        tmp_df = self.get_table_df(self.config.get('AUTH', 'PNO'), ['ID'], conditions=pno_conds)
        
        self.delete_ids_from_table(self.config.get('DEPENDENCIES', 'OFO'), pnoids, 'PNOID')
        
        pno_conds = [f"ID = '{pnoids[0]}'"] if len(pnoids) == 1 else [f"ID IN {tuple(pnoids)}"]
        if tmp_df.empty:
            return
        self.delete_ids_from_table(self.config.get('RELATIONS', 'PNO_Custom'), pnoids, 'RelationID')
        self.delete_ids_from_table(self.config.get('AUTH', 'PNO'), pnoids, 'ID')

    def collect_dependency(self, df, df_pnos):
        df_assigned, df_unassigned = utils.get_pno_ids_from_variants(df_pnos, df, is_relation=False)
        utils.log_df(df_unassigned, 'Dependencies from CPAM were not assigned to any existing authorized PNOs. Should have been removed as it was deauthorized::', self.logger.error)

        df_final = df_assigned.explode('FeatureCode')
        df_final.insert(2, 'RuleName', df_final['RuleCode'].map(lambda x: self.config.get('DEPENDENCIES_NAMES', x)))

        dependency_columns = ['PNOID', 'RuleCode', 'RuleName', 'ItemCode', 'FeatureCode', 'StartDate', 'EndDate']
        dependency_conditional_columns = ['PNOID', 'RuleCode', 'ItemCode', 'FeatureCode', 'StartDate']
        self.logger.info('Inserting dependencies')
        df_final['RuleCodeTable'] = df_final['RuleCode'].map(lambda x: self.config.get('DEPENDENCIES', x))
        for data_type, group in df_final.groupby('RuleCodeTable'):
            group = group.drop('RuleCodeTable', axis=1)
            self.upsert_data_from_df(group, data_type, dependency_columns, dependency_conditional_columns)

    def drop_dependency(self, df, df_pnos):
        df_assigned, _ = utils.get_pno_ids_from_variants(df_pnos, df, is_relation=False)
        if df_assigned.empty:
            self.logger.info('No dependencies to delete')
            return
        
        df_final = df_assigned.explode('FeatureCode')
        df_final['RuleCodeTable'] = df_final['RuleCode'].map(lambda x: self.config.get('DEPENDENCIES', x))
        
        for data_type, group in df_final.groupby('RuleCodeTable'):
            filter_func = lambda row: f"ItemCode = '{row['ItemCode']}' AND FeatureCode = '{row['FeatureCode']}'" if group.shape[0] == 1 else f"(ItemCode = '{row['ItemCode']}' AND FeatureCode = '{row['FeatureCode']}')"
            group = group.drop('RuleCodeTable', axis=1)
            group['Condition'] = group.apply(filter_func, axis=1)
            # group by PNOID and RuleCode
            group = group.groupby(['PNOID'])['Condition'].apply(lambda x: ' OR '.join(x)).reset_index()
            
            conditions = group['Condition'].unique().tolist()
            
            all_ids = []
            chunk_size = 100
            for i in range(0, len(conditions), chunk_size):
                chunk = conditions[i:i+chunk_size]
                or_conditions = [' OR '.join(chunk)]
                df_inserted = self.get_table_df(data_type, columns=['ID'], conditions=or_conditions)
                ids = df_inserted['ID'].unique().tolist()
                if ids:
                    all_ids.extend(ids)
            if all_ids:
                self.delete_ids_from_table(data_type, all_ids, 'ID')
            else:
                self.logger.info('No dependencies to delete')
    
    def collect_feature(self, df, df_pnos):
        df_assigned, df_unassigned = utils.get_pno_ids_from_variants(df_pnos, df)
        utils.log_df(df_unassigned, 'Feature from CPAM were not assigned to any existing authorized PNOs. Should have been removed as it was deauthorized::', self.logger.error)

        # Column reference might include comma seperated values: split then explode
        df_assigned['Reference'] = df_assigned['Reference'].str.split(',')
        df_assigned = df_assigned.explode('Reference')
        df_assigned = df_assigned.fillna('')

        feature_columns = ['PNOID', 'Code', 'Special', 'Reference', 'Options', 'RuleName', 'StartDate', 'EndDate']
        feature_conditional_columns = ['PNOID', 'Code', 'StartDate']
        self.logger.info('Inserting features')
        self.upsert_data_from_df(df_assigned, self.config.get('AUTH', 'FEAT'), feature_columns, feature_conditional_columns)
    
    def drop_feature(self, df, df_pnos):
        df_assigned, _ = utils.get_pno_ids_from_variants(df_pnos, df)
        if df_assigned.empty:
            self.logger.info('No features to delete')
            return
        
        self.logger.info('Deleting features')
        filter_func = lambda row: f"PNOID = '{row['PNOID']}' AND Code = '{row['Code']}'" if df_assigned.shape[0] == 1 else f"(PNOID = '{row['PNOID']}' AND Code = '{row['Code']}')"
        
        df_assigned['Condition'] = df_assigned.apply(filter_func, axis=1)
        conditions = df_assigned['Condition'].unique().tolist()
        all_ids = []
        chunk_size = 100
        for i in range(0, len(conditions), chunk_size):
            chunk = conditions[i:i+chunk_size]
            or_conditions = [' OR '.join(chunk)]
            df_inserted = self.get_table_df(self.config.get('AUTH', 'FEAT'), columns=['ID'], conditions=or_conditions)
            ids = df_inserted['ID'].unique().tolist()
            if ids:
                all_ids.extend(ids)
        if all_ids:
            self.delete_ids_from_table(self.config.get('AUTH', 'FEAT'), all_ids, 'ID')
        else:
            self.logger.info('No dependencies to delete')

    def collect_package(self, df, df_pnos):
        df['StartDate'] = df['StartDate'].astype(int)
        df['EndDate'] = df['EndDate'].astype(int)

        df_assigned, df_unassigned = utils.get_pno_ids_from_variants(df_pnos, df)
        df_assigned = df_assigned.fillna('')
        utils.log_df(df_unassigned, 'Package from CPAM were not assigned to any existing authorized PNOs. Should have been removed as it was deauthorized:', self.logger.error)
        
        package_columns = ['PNOID', 'Code', 'Title', 'RuleCode', 'RuleType', 'RuleName', 'RuleBase', 'StartDate', 'EndDate']
        package_conditional_columns = ['PNOID', 'Code', 'RuleCode', 'StartDate']
        self.logger.info('Inserting packages')
        self.upsert_data_from_df(df_assigned, self.config.get('AUTH', 'PKG'), package_columns, package_conditional_columns)
        pno_ids = df_assigned['PNOID'].unique().tolist()
        
        conditions = []
        if len(pno_ids) == 1:
            conditions.append(f"PNOID = '{pno_ids[0]}'")
        else:
            conditions.append(f"PNOID in {tuple(pno_ids)}")
        df_inserted = self.get_table_df(self.config.get('AUTH', 'PKG'), columns=['ID as RelationID', 'Code', 'StartDate', 'EndDate'], conditions=conditions)
        ids = df_inserted['RelationID'].unique().tolist()
        conditions = []
        if len(ids) == 1:
            conditions.append(f"RelationID = '{ids[0]}'")
        else:
            conditions.append(f"RelationID in {tuple(ids)}")
        df_relation = self.get_table_df(self.config.get('RELATIONS', 'PKG_Custom'), conditions=conditions)
        if df_relation.empty:
            df_inserted['CustomName'] = ''
            self.upsert_data_from_df(df_inserted, self.config.get('RELATIONS', 'PKG_Custom'), ['RelationID', 'CustomName', 'StartDate', 'EndDate'], ['RelationID'])
            return
        df_relation = df_relation.drop(['StartDate', 'EndDate'], axis=1)
        df_inserted = df_inserted.merge(df_relation, on=['RelationID'], how='left')
        
        df_inserted['CustomName'] = df_inserted.groupby('Code').apply(utils.fill_custom_name).reset_index(drop=True)
        self.upsert_data_from_df(df_inserted, self.config.get('RELATIONS', 'PKG_Custom'), ['RelationID', 'CustomName', 'StartDate', 'EndDate'], ['RelationID'])

    def assign_prices_from_visa_dataframe(self, country_code, df_visa):
        if df_visa.empty:
            self.logger.info("No VISA data found")
            return
        df_all_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f"CountryCode='{country_code}'"])
        df_all_pnos = df_all_pnos.drop('CountryCode', axis=1)
        for model_year in df_visa['ModelYear'].unique():
            model_year = int(model_year)
            df_pnos = utils.filter_df_by_model_year(df_all_pnos, model_year)
            if df_pnos.empty:
                self.logger.info("No existing PNOs found. It doesn't make sense to proceed without PNOs")
                return
            
            # Split the DataFrame into multiple DataFrames
            df_pno_prices, df_color_pno_prices, df_option_pno_prices, df_upholstery_pno_prices, df_package_pno_prices = utils.split_df(df_visa)
            
            relation_columns = ['RelationID', 'StartDate', 'EndDate', 'Price', 'PriceBeforeTax']
            conditional_columns = ['RelationID']

            if not df_pno_prices.empty:
                df_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_pno_prices, is_relation=True)
                df_pnos_assigned = df_pnos_assigned.drop_duplicates(subset=['RelationID', 'StartDate'], keep='last')
                self.upsert_data_from_df(df_pnos_assigned, self.config.get('RELATIONS', 'PNO_Custom'), relation_columns, conditional_columns)
                utils.log_df(df_pnos_unassigned, 'PNO in VISA File did not match CPAM PNOs:', self.logger.warning, country_code=country_code)        
            
            if not df_color_pno_prices.empty:
                df_color_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_color_pno_prices, is_relation=False)
                df_color_pnos_assigned = df_color_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last')
                df_colors = self.get_table_df(self.config.get('AUTH', 'COL'))
                df_color, df_color_unpriced = utils.get_relation_ids(df_colors, df_color_pnos_assigned)
                self.upsert_data_from_df(df_color, self.config.get('RELATIONS', 'COL_Custom'), relation_columns, conditional_columns)
                utils.log_df(df_pnos_unassigned, 'PNO in VISA File did not match CPAM PNOs:', self.logger.warning, country_code=country_code)
                utils.log_df(df_color_unpriced, 'Color from VISA file did not find an authorized match in CPAM: ', self.logger.warning, country_code=country_code)

            if not df_option_pno_prices.empty:
                df_option_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_option_pno_prices, is_relation=False)
                df_option_pnos_assigned = df_option_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last')
                df_options = self.get_table_df(self.config.get('AUTH', 'OPT'))
                df_option, df_option_unpriced = utils.get_relation_ids(df_options, df_option_pnos_assigned)
                self.upsert_data_from_df(df_option, self.config.get('RELATIONS', 'OPT_Custom'), relation_columns, conditional_columns)
                utils.log_df(df_pnos_unassigned, 'PNO in VISA File did not match CPAM PNOs:', self.logger.warning, country_code=country_code)
                utils.log_df(df_option_unpriced, 'Option frpm VISA file did not find an authorized match in CPAM: ', self.logger.warning, country_code=country_code)

            if not df_upholstery_pno_prices.empty:
                df_upholstery_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_upholstery_pno_prices, is_relation=False)
                df_upholstery_pnos_assigned = df_upholstery_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last')
                df_upholsteries = self.get_table_df(self.config.get('AUTH', 'UPH'))
                df_upholstery, df_upholstery_unpriced = utils.get_relation_ids(df_upholsteries, df_upholstery_pnos_assigned)
                self.upsert_data_from_df(df_upholstery, self.config.get('RELATIONS', 'UPH_Custom'), relation_columns, conditional_columns)
                utils.log_df(df_pnos_unassigned, 'PNO in VISA File did not match CPAM PNOs:', self.logger.warning, country_code=country_code)
                utils.log_df(df_upholstery_unpriced, 'Upholstery from VISA file did not find an authorized match in CPAM: ', self.logger.warning, country_code=country_code)
            
            if not df_package_pno_prices.empty:
                df_package_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_package_pno_prices, is_relation=False)
                df_package_pnos_assigned = df_package_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last')
                df_packages = self.get_table_df(self.config.get('AUTH', 'PKG'))
                df_package, df_package_unpriced = utils.get_relation_ids(df_packages, df_package_pnos_assigned)
                self.upsert_data_from_df(df_package, self.config.get('RELATIONS', 'PKG_Custom'), relation_columns, conditional_columns)
                utils.log_df(df_pnos_unassigned, 'PNO in VISA File did not match CPAM PNOs:', self.logger.warning, country_code=country_code)
                utils.log_df(df_package_unpriced, 'Package from VISA file did not find an authorized match in CPAM: ', self.logger.warning, country_code=country_code)

    def consolidate_translations(self, country_code):
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f"CountryCode='{country_code}'"])
        if df_pnos.empty:
            self.logger.warning("No existing PNOs found. No translations to consolidate", extra={'country_code': country_code})
            return
        pno_ids = df_pnos['ID'].unique().tolist()
        conds = []
        if len(pno_ids) == 1:
            conds.append(f"PNOID = '{pno_ids[0]}'")
        else:
            conds.append(f"PNOID in {tuple(pno_ids)}")
        
        ## Color, upholstery and package translations
        for data_type in ['COL', 'UPH', 'PKG']:
            
            df_codes = self.get_table_df(self.config.get('AUTH', data_type), columns=['ID', 'Code'], conditions=conds)
            all_ids = df_codes['ID'].unique().tolist()
            # Fetch every 5000 ids at a time
            df_all_translation = pd.DataFrame()
            chunk_size = 5000
            for i in range(0, len(all_ids), chunk_size):
                ids = all_ids[i:i+chunk_size]
                conditions=[]
                if len(ids) == 1:
                    conditions.append(f"RelationID = '{ids[0]}'")
                else:
                    conditions.append(f"RelationID in {tuple(ids)}")
                
                table_name = self.config.get('RELATIONS', f'{data_type}_Custom')
                df_part_translation = self.get_table_df(table_name, columns=['RelationID', 'CustomName'], conditions=conditions)
                df_all_translation = pd.concat([df_all_translation, df_part_translation])
            
            if df_all_translation[(df_all_translation['CustomName'].isnull()) | (df_all_translation['CustomName'] == '')].empty:
                self.logger.warning(f"No empty translations in {table_name} were found", extra={'country_code': country_code})
                continue
            
            df_merge = df_all_translation.merge(df_codes, left_on='RelationID', right_on='ID', how='left')
            
            # Drop where CustomName is empty or null
            df_merge_translation_source = df_merge[(~df_merge['CustomName'].isnull()) & (df_merge['CustomName'] != '')]

            df_merge = df_merge.drop(['ID', 'CustomName'], axis=1)
            
            # Group by code and get the custom name, if only one non empty custom name is found.
            df_translation = df_merge_translation_source.groupby('Code')['CustomName'].unique().apply(lambda x: x[0] if len(x) == 1 else '').reset_index()
            df_translation = df_translation[df_translation['CustomName'] != '']
            
            df_fin = df_merge.merge(df_translation, on='Code', how='left')
            df_fin = df_fin.drop('Code', axis=1)
            df_fin = df_fin.fillna('')
            
            self.upsert_data_from_df(df_fin, table_name, ['RelationID', 'CustomName'], ['RelationID'])
        
        ## Upholstery category translations
        data_type = 'UPH'
        df_codes = self.get_table_df(self.config.get('AUTH', data_type), columns=['ID', 'Code'], conditions=conds)
        ids = df_codes['ID'].unique().tolist()
        
        conditions=[]
        if len(ids) == 1:
            conditions.append(f"RelationID = '{ids[0]}'")
        else:
            conditions.append(f"RelationID in {tuple(ids)}")
        
        table_name = self.config.get('RELATIONS', f'{data_type}_Custom')
        df_all_translation = self.get_table_df(table_name, columns=['RelationID', 'CustomCategory'], conditions=conditions)
        
        df_needs_translation = df_all_translation[(df_all_translation['CustomCategory'].isnull()) | (df_all_translation['CustomCategory'] == '')]
        if not df_needs_translation.empty:
            df_needs_translation = df_needs_translation.drop('CustomCategory', axis=1)
            
            df_merge = df_all_translation.merge(df_codes, left_on='RelationID', right_on='ID', how='inner')
            
            # Drop where CustomCategory is empty or null
            df_merge_translation_source = df_merge[(~df_merge['CustomCategory'].isnull()) & (df_merge['CustomCategory'] != '')]

            df_merge = df_merge.drop(['ID', 'CustomCategory'], axis=1)
            
            # Group by code and get the custom name, if only one non empty custom name is found.
            df_translation = df_merge_translation_source.groupby('Code')['CustomCategory'].unique().apply(lambda x: x[0] if len(x) == 1 else '').reset_index()
            df_translation = df_translation[df_translation['CustomCategory'] != '']
            
            df_fin = df_merge.merge(df_translation, on='Code', how='inner')
            df_fin = df_fin.drop('Code', axis=1)
            df_fin = df_fin.fillna('')
            
            self.upsert_data_from_df(df_fin, table_name, ['RelationID', 'CustomCategory'], ['RelationID'])
        else:
            self.logger.warning(f"No empty translations in {table_name} were found", extra={'country_code': country_code})
        
        ## Feature translation
        data_type = 'FEAT'
        df_codes = self.get_table_df(self.config.get('AUTH', data_type), columns=['ID', 'Code', 'CustomName', 'CustomCategory'], conditions=conds)
        
        for att in ['CustomName', 'CustomCategory']:
            df_att = df_codes[['ID', 'Code', att]]
            df_att_translation = df_att[(~df_att[att].isnull()) & (df_att[att] != '')]
            df_att_needs_translation = df_att[(df_att[att].isnull()) | (df_att[att] == '')]
            if df_att_needs_translation.empty:
                self.logger.warning(f"No empty translations in {att} were found", extra={'country_code': country_code})
                continue
            df_att_needs_translation = df_att_needs_translation.drop(att, axis=1)
            
            df_translation = df_att_translation.groupby('Code')[att].unique().apply(lambda x: x[0] if len(x) == 1 else '').reset_index()
            
            df_translation = df_translation[df_translation[att] != '']
            
            df_fin = df_att_needs_translation.merge(df_translation, on='Code', how='inner')
            df_fin = df_fin.drop('Code', axis=1)
            df_fin = df_fin.fillna('')
            
            self.upsert_data_from_df(df_fin, self.config.get('AUTH', data_type), ['ID', att], ['ID'])
