from cachetools import cached, TTLCache
from contextlib import contextmanager
import configparser
import pandas as pd
import logging

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
        
        if conditions is None:
            conditions = '1=1'
        elif isinstance(conditions, list):
            conditions = ' AND '.join(conditions)
        else:
            raise ValueError('Conditions must be a list')
        
        return self.get_table_df_cached(table_name, columns, conditions)
        
    @cached(cache)
    def get_table_df_cached(self, table_name, columns, conditions):
        
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

        df.drop_duplicates(subset=conditional_columns, inplace=True)

        with self.get_cursor() as cursor:
            # Causing errors in PROD
            cursor.fast_executemany = False

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
            cursor.executemany(sql, params)

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

    def collect_entity(self, datarows, country_code):
        if not datarows:
            self.logger.warning('No data to insert')
            return False
        df = pd.DataFrame(datarows)
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
            self.upsert_data_from_df(group, table_name, entity_columns, conditional_columns)

        return True

    def collect_auth(self, datarows, country_code):
        df = utils.df_from_datarows(datarows, ['Code', 'DataType'])

        df_pno = df[df['DataType'] == 'PNO'].copy()
        df_pno.insert(9, 'CountryCode', country_code)
        df = df[df['DataType'] != 'PNO'].copy()

        self.logger.debug('Inserting PNOs')
        pno_columns = ['Code', 'Model', 'Engine', 'SalesVersion', 'Steering', 'Gearbox', 'Body', 'MarketCode', 'CountryCode', 'StartDate', 'EndDate']
        conditional_columns = ['Code', 'CountryCode', 'StartDate']
        df_pno = df_pno.drop(['RuleName', 'DataType'], axis=1)
        self.upsert_data_from_df(df_pno, self.config.get('AUTH', 'PNO'), pno_columns, conditional_columns)
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f"CountryCode='{country_code}'"])
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.warning("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return

        df_assigned, df_unassigned = utils.get_pno_ids_from_variants(df_pnos, df)
        utils.log_df(df_unassigned, 'Packages from CPAM were not assigned to any existing authorized PNOs:', self.logger.warning)
        
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
            conditions = []
            if len(pno_ids) == 1:
                conditions.append(f"RelationID = '{pno_ids[0]}'")
            else:
                conditions.append(f"RelationID in {tuple(pno_ids)}")
            df_relation = self.get_table_df(self.config.get('RELATIONS', f'{data_type}_Custom'), conditions=conditions)
            if df_relation.empty:
                df_inserted['CustomName'] = ''
                self.upsert_data_from_df(df_inserted, self.config.get('RELATIONS', f'{data_type}_Custom'), ['RelationID', 'StartDate', 'EndDate'], ['RelationID'])
                continue
            df_inserted = df_inserted.merge(df_relation, on=['RelationID'], how='left', indicator=True)
            
            group['CustomName'] = group.groupby('Code').apply(utils.fill_custom_name).reset_index(drop=True)
            self.upsert_data_from_df(df_inserted, self.config.get('RELATIONS', f'{data_type}_Custom'), ['RelationID', 'CustomName', 'StartDate', 'EndDate'], ['RelationID'])

    def collect_dependency(self, datarows, country_code):
        if not datarows:
            self.logger.debug('No data to insert')
            return
        df = utils.df_from_datarows(datarows, ['RuleCode', 'ItemCode', 'FeatureCode'])
        
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f"CountryCode='{country_code}'"])
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.warning("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return

        df_assigned, df_unassigned = utils.get_pno_ids_from_variants(df_pnos, df, is_relation=False)
        utils.log_df(df_unassigned, 'Packages from CPAM were not assigned to any existing authorized PNOs:', self.logger.warning)

        df_final = df_assigned.explode('FeatureCode')
        df_final.insert(2, 'RuleName', df_final['RuleCode'].map(lambda x: self.config.get('DEPENDENCIES_NAMES', x)))

        dependency_columns = ['PNOID', 'RuleCode', 'RuleName', 'ItemCode', 'FeatureCode', 'StartDate', 'EndDate']
        dependency_conditional_columns = ['PNOID', 'RuleCode', 'ItemCode', 'FeatureCode', 'StartDate']
        self.logger.info('Inserting dependencies')
        for data_type, group in df_final.groupby('RuleCode'):
            self.upsert_data_from_df(group, self.config.get('DEPENDENCIES', data_type), dependency_columns, dependency_conditional_columns)

    def collect_feature(self, datarows, country_code):
        if not datarows:
            self.logger.info('No data to insert')
            return
        df = utils.df_from_datarows(datarows, ['Code', 'Special', 'Reference'])
        df['Code'] = df['Code'].str.strip()
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f"CountryCode='{country_code}'"])
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.info("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return

        df_assigned, df_unassigned = utils.get_pno_ids_from_variants(df_pnos, df)
        utils.log_df(df_unassigned, 'Feature from CPAM were not assigned to any existing authorized PNOs:', self.logger.warning)

        # column reference might include comma seperated values: split then explode
        df_assigned['Reference'] = df_assigned['Reference'].str.split(',')
        df_assigned = df_assigned.explode('Reference')

        feature_columns = ['PNOID', 'Code', 'Special', 'Reference', 'Options', 'RuleName', 'StartDate', 'EndDate']
        
        feature_conditional_columns = ['PNOID', 'Code', 'StartDate']
        self.logger.info('Inserting features')
        self.upsert_data_from_df(df_assigned, self.config.get('AUTH', 'FEAT'), feature_columns, feature_conditional_columns)

    def collect_package(self, datarows, country_code):
        if not datarows:
            self.logger.info('No data to insert')
            return
        
        df = utils.df_from_package_datarows(datarows)
        df['StartDate'] = df['StartDate'].astype(int)
        df['EndDate'] = df['EndDate'].astype(int)
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f"CountryCode='{country_code}'"])
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.info("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return

        df_assigned, df_unassigned = utils.get_pno_ids_from_variants(df_pnos, df)
        utils.log_df(df_unassigned, 'Package from CPAM were not assigned to any existing authorized PNOs:', self.logger.warning)
        
        package_columns = ['PNOID', 'Code', 'Title', 'RuleCode', 'RuleType', 'RuleName', 'RuleBase', 'StartDate', 'EndDate']
        package_conditional_columns = ['PNOID', 'Code', 'RuleCode', 'StartDate']
        self.logger.info('Inserting packages')
        self.upsert_data_from_df(df_assigned, self.config.get('AUTH', 'PKG'), package_columns, package_conditional_columns)

    def assign_prices_from_visa_dataframe(self, country_code, df_visa):
        if df_visa.empty:
            self.logger.info("No VISA data found")
            return
        df_all_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f"CountryCode='{country_code}'"])
        df_pnos = df_all_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.info("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return
        
        # Split the DataFrame into multiple DataFrames
        df_pno_prices, df_color_pno_prices, df_option_pno_prices, df_upholstery_pno_prices, df_package_pno_prices = utils.split_df(df_visa)
        
        relation_columns = ['RelationID', 'StartDate', 'EndDate', 'Price', 'PriceBeforeTax']
        conditional_columns = ['RelationID', 'StartDate']

        if not df_pno_prices.empty:
            df_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_pno_prices, is_relation=True)
            df_pnos_assigned.drop_duplicates(subset=['RelationID', 'StartDate'], keep='last', inplace=True)
            self.upsert_data_from_df(df_pnos_assigned, self.config.get('RELATIONS', 'PNO_Custom'), relation_columns, conditional_columns)
            utils.log_df(df_pnos_unassigned, 'PNOs from Visa file unassigned to CPAM PNOs:', self.logger.warning, country_code=country_code)          
        
        if not df_color_pno_prices.empty:
            df_color_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_color_pno_prices, is_relation=False)
            df_color_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last', inplace=True)
            df_colors = self.get_table_df(self.config.get('AUTH', 'COL'))
            df_color, df_color_unpriced = utils.get_relation_ids(df_colors, df_color_pnos_assigned)
            self.upsert_data_from_df(df_color, self.config.get('RELATIONS', 'COL_Custom'), relation_columns, conditional_columns)
            utils.log_df(df_pnos_unassigned, 'PNOs from Visa file unassigned to CPAM PNOs:', self.logger.warning, country_code=country_code)
            utils.log_df(df_color_unpriced, 'Colors from CPAM did not find a price in the Visa file: ', self.logger.warning, country_code=country_code)

        if not df_option_pno_prices.empty:
            df_option_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_option_pno_prices, is_relation=False)
            df_option_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last', inplace=True)
            df_options = self.get_table_df(self.config.get('AUTH', 'OPT'))
            df_option, df_option_unpriced = utils.get_relation_ids(df_options, df_option_pnos_assigned)
            self.upsert_data_from_df(df_option, self.config.get('RELATIONS', 'OPT_Custom'), relation_columns, conditional_columns)
            utils.log_df(df_pnos_unassigned, 'PNOs from Visa file unassigned to CPAM PNOs:', self.logger.warning, country_code=country_code)
            utils.log_df(df_option_unpriced, 'Options from CPAM did not find a price in the Visa file: ', self.logger.warning, country_code=country_code)

        if not df_upholstery_pno_prices.empty:
            df_upholstery_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_upholstery_pno_prices, is_relation=False)
            df_upholstery_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last', inplace=True)
            df_upholsteries = self.get_table_df(self.config.get('AUTH', 'UPH'))
            df_upholstery, df_upholstery_unpriced = utils.get_relation_ids(df_upholsteries, df_upholstery_pnos_assigned)
            self.upsert_data_from_df(df_upholstery, self.config.get('RELATIONS', 'UPH_Custom'), relation_columns, conditional_columns)
            utils.log_df(df_pnos_unassigned, 'PNOs from Visa file unassigned to CPAM PNOs:', self.logger.warning, country_code=country_code)
            utils.log_df(df_upholstery_unpriced, 'Upholsteries from CPAM did not find a price in the Visa file: ', self.logger.warning, country_code=country_code)
        
        if not df_package_pno_prices.empty:
            df_package_pnos_assigned, df_pnos_unassigned = utils.get_pno_ids_from_variants(df_pnos, df_package_pno_prices, is_relation=False)
            df_package_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last', inplace=True)
            df_packages = self.get_table_df(self.config.get('AUTH', 'PKG'))
            df_package, df_package_unpriced = utils.get_relation_ids(df_packages, df_package_pnos_assigned)
            self.upsert_data_from_df(df_package, self.config.get('RELATIONS', 'PKG_Custom'), relation_columns, conditional_columns)
            utils.log_df(df_pnos_unassigned, 'PNOs from Visa file unassigned to CPAM PNOs:', self.logger.warning, country_code=country_code)
            utils.log_df(df_package_unpriced, 'Packages from CPAM did not find a price in the Visa file: ', self.logger.warning, country_code=country_code)
