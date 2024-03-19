import logging
import configparser
from contextlib import contextmanager
import pandas as pd
from src.database.db_connection import DatabaseConnection
from src.utils.db_utils import df_from_datarows, df_from_package_datarows, filter_df_by_model_year, get_pno_ids_from_variants, get_relation_ids, split_df


class DBOperations:
    instance = None

    @classmethod
    def create_instance(cls):
        if cls.instance is None:
            config = configparser.ConfigParser()
            config.read('config/data_model.cfg')
            conn = DatabaseConnection.get_db_connection()
            cls.instance = cls(conn, config)
        return cls.instance
    
    def __init__(self, db_conn, config):
        self.conn = db_conn
        self.config = config
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.conn.close()

    @contextmanager
    def get_cursor(self):
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.logger.error('Database operation failed', exc_info=True)
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
        
        with self.get_cursor() as cursor:
            cursor.execute(f"SELECT {columns} FROM {table_name}")
            data = cursor.fetchall()
            if not data:
                return pd.DataFrame()
            columns = [column[0] for column in data[0].cursor_description]
            data = [list(row) for row in data]
            df = pd.DataFrame(data, columns=columns)
            return df

    def upsert_data_from_df(self, df, table_name, columns, conditional_columns):
        self.create_temp_staging_table(table_name, columns)
        self.insert_data_into_staging(table_name, df, columns, conditional_columns)
        self.merge_data_from_staging(table_name, columns, conditional_columns)
        self.drop_temp_staging_table(table_name)

    def create_temp_staging_table(self, target_table_name, cols):
        try:
            with self.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT {', '.join(cols)} 
                    INTO #tmp_staging_{target_table_name}
                    FROM {target_table_name}
                    WHERE 1=0;
                """)
        except Exception as e:
            self.logger.error(f"Error creating temporary staging table: {e}")
            raise e

    def insert_data_into_staging(self, target_table_name, df, columns, conditional_columns=None):
        # Ensure the DataFrame is not empty
        if df.empty:
            self.logger.error("The DataFrame is empty. No data to insert.")
            return
        
        if not conditional_columns:
            conditional_columns = ['Code', 'StartDate']
        df.drop_duplicates(subset=conditional_columns, inplace=True)

        with self.get_cursor() as cursor:
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

    def log_change_from_staging(self, target_table_name):
        try:
            with self.get_cursor() as cursor:
                changelog_table_name = f"{target_table_name}_ChangeLog"
                cursor.execute(f"""
                    INSERT INTO {changelog_table_name} (Code, StartDate, OldSpecial, NewSpecial, ChangeDate)
                    SELECT TARGET.Code, TARGET.StartDate, TARGET.Special, SOURCE.Special, CURRENT_TIMESTAMP
                    FROM {target_table_name} AS TARGET
                    JOIN #tmp_staging_{target_table_name} AS SOURCE
                    ON TARGET.Code = SOURCE.Code AND TARGET.StartDate = SOURCE.StartDate
                    WHERE TARGET.Special <> SOURCE.Special;
                """)
        except Exception as e:
            self.logger.error(f"Error merging data from temporary staging table: {e}")

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
                    WHEN MATCHED THEN
                        UPDATE SET {update_sql}
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

    def collect_entity(self, datarows, spec_market):
        if not datarows:
            self.logger.info('No data to insert')
            return False
        df = pd.DataFrame(datarows)
        df['DataType'] = df.apply(lambda row: row['MainDataType'] if row['DataType'] == '' else row['DataType'], axis=1)
        df = df.drop('MainDataType', axis=1)
        df.insert(5, 'CountryCode', spec_market)

        self.logger.info('Inserting entities')
        entity_columns = ['Code', 'Special', 'ShortText', 'MarketText', 'CountryCode', 'StartDate', 'EndDate']
        for data_type, group in df.groupby('DataType'):
            table_name = self.config.get('TABLES', data_type)
            if table_name=='Feature':
                conditional_columns = ['Code', 'Special', 'CountryCode', 'StartDate']
            else:
                conditional_columns = ['Code', 'CountryCode', 'StartDate']
            group = group.drop('DataType', axis=1)
            self.upsert_data_from_df(group, table_name, entity_columns, conditional_columns)

        return True

    def collect_auth(self, datarows, spec_market):
        df = df_from_datarows(datarows, ['Code', 'DataType'])

        df_pno = df[df['DataType'] == 'PNO'].copy()
        df_pno.insert(9, 'CountryCode', spec_market)
        df = df[df['DataType'] != 'PNO'].copy()

        self.logger.info('Inserting PNOs')
        pno_columns = ['Code', 'Model', 'Engine', 'SalesVersion', 'Steering', 'Gearbox', 'Body', 'MarketCode', 'CountryCode', 'StartDate', 'EndDate']
        conditional_columns = ['Code', 'CountryCode', 'StartDate']
        df_pno = df_pno.drop(['RuleName', 'DataType'], axis=1)
        self.upsert_data_from_df(df_pno, self.config.get('AUTH', 'PNO'), pno_columns, conditional_columns)
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f'CountryCode={spec_market}'])
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.info("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return

        df_assigned, df_unassigned = get_pno_ids_from_variants(df_pnos, df)
        
        auth_columns = ['PNOID', 'Code', 'RuleName', 'StartDate', 'EndDate']
        auth_conditional_columns = ['PNOID', 'Code', 'StartDate']
        self.logger.info('Inserting authorizations')
        for data_type, group in df_assigned.groupby('DataType'):
            group = group.drop('DataType', axis=1)
            self.upsert_data_from_df(group, self.config.get('AUTH', data_type), auth_columns, auth_conditional_columns)

    def collect_dependency(self, datarows, spec_market):
        if not datarows:
            self.logger.info('No data to insert')
            return
        df = df_from_datarows(datarows, ['RuleCode', 'ItemCode', 'FeatureCode'])
        
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f'CountryCode={spec_market}'])
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.info("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return

        df_assigned, df_unassigned = get_pno_ids_from_variants(df_pnos, df, is_relation=False)

        df_final = df_assigned.explode('FeatureCode')
        df_final.insert(2, 'RuleName', df_final['RuleCode'].map(lambda x: self.config.get('DEPENDENCIES_NAMES', x)))

        dependency_columns = ['PNOID', 'RuleCode', 'RuleName', 'ItemCode', 'FeatureCode', 'StartDate', 'EndDate']
        dependency_conditional_columns = ['PNOID', 'RuleCode', 'ItemCode', 'FeatureCode', 'StartDate']
        self.logger.info('Inserting dependencies')
        for data_type, group in df_final.groupby('RuleCode'):
            self.upsert_data_from_df(group, self.config.get('DEPENDENCIES', data_type), dependency_columns, dependency_conditional_columns)

    def collect_feature(self, datarows, spec_market):
        if not datarows:
            self.logger.info('No data to insert')
            return
        df = df_from_datarows(datarows, ['Code', 'Special', 'Reference'])
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f'CountryCode={spec_market}'])
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.info("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return

        df_assigned, df_unassigned = get_pno_ids_from_variants(df_pnos, df)
        # column reference might include comma seperated values: split then explode
        df_assigned['Reference'] = df_assigned['Reference'].str.split(',')
        df_assigned = df_assigned.explode('Reference')

        feature_columns = ['PNOID', 'Code', 'Special', 'Reference', 'Options', 'RuleName', 'StartDate', 'EndDate']
        
        feature_conditional_columns = ['PNOID', 'Code', 'StartDate']
        self.logger.info('Inserting features')
        self.upsert_data_from_df(df_assigned, self.config.get('AUTH', 'FEAT'), feature_columns, feature_conditional_columns)

    def collect_package(self, datarows, spec_market):
        if not datarows:
            self.logger.info('No data to insert')
            return
        
        df = df_from_package_datarows(datarows)
        df['StartDate'] = df['StartDate'].astype(int)
        df['EndDate'] = df['EndDate'].astype(int)
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f'CountryCode={spec_market}'])
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.info("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return

        df_assigned, df_unassigned = get_pno_ids_from_variants(df_pnos, df)
        
        package_columns = ['PNOID', 'Code', 'Title', 'RuleCode', 'RuleType', 'RuleName', 'RuleBase', 'StartDate', 'EndDate']
        package_conditional_columns = ['PNOID', 'Code', 'RuleCode', 'StartDate']
        self.logger.info('Inserting packages')
        self.upsert_data_from_df(df_assigned, self.config.get('AUTH', 'PKG'), package_columns, package_conditional_columns)

    def assign_prices_from_visa_dataframe(self, spec_market):
        df_pnos = self.get_table_df(self.config.get('AUTH', 'PNO'), conditions=[f'CountryCode={spec_market}'])
        df_pnos = df_pnos.drop('CountryCode', axis=1)
        if df_pnos.empty:
            self.logger.info("No existing PNOs found. It doesn't make sense to proceed without PNOs")
            return
        
        df_visa = self.get_table_df(self.config.get('RELATIONS', 'VISA'), [f'MarketCode={spec_market}'])

        # Iterate over each model year prices
        for my, group in df_visa.groupby(df_visa['ModelYear']):
            # Drop the 'ModelYear' column from the group
            group = group.drop(columns=['ModelYear'])
            df_pnos = filter_df_by_model_year(df_pnos, my)

            # Split the DataFrame into multiple DataFrames
            df_pno_prices, df_color_pno_prices, df_option_pno_prices, df_upholstery_pno_prices, df_package_pno_prices = split_df(group)
            
            relation_columns = ['RelationID', 'StartDate', 'EndDate', 'Price', 'PriceBeforeTax']
            conditional_columns = ['RelationID', 'StartDate']

            df_pnos_assigned, df_pnos_unassigned = get_pno_ids_from_variants(df_pnos, df_pno_prices, is_relation=True)
            df_pnos_assigned.drop_duplicates(subset=['RelationID', 'StartDate'], keep='last', inplace=True)
            self.upsert_data_from_df(df_pnos_assigned, self.config.get('RELATIONS', 'PNO_Custom'), relation_columns, conditional_columns)
            
            df_color_pnos_assigned, df_pnos_unassigned = get_pno_ids_from_variants(df_pnos, df_color_pno_prices, is_relation=False)
            df_color_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last', inplace=True)
            df_colors = self.get_table_df(self.config.get('AUTH', 'COL'))
            df_color = get_relation_ids(df_colors, df_color_pnos_assigned)
            self.upsert_data_from_df(df_color, self.config.get('RELATIONS', 'COL_Custom'), relation_columns, conditional_columns)

            df_option_pnos_assigned, df_pnos_unassigned = get_pno_ids_from_variants(df_pnos, df_option_pno_prices, is_relation=False)
            df_option_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last', inplace=True)
            df_options = self.get_table_df(self.config.get('AUTH', 'OPT'))
            df_option = get_relation_ids(df_options, df_option_pnos_assigned)
            self.upsert_data_from_df(df_option, self.config.get('RELATIONS', 'OPT_Custom'), relation_columns, conditional_columns)

            df_upholstery_pnos_assigned, df_pnos_unassigned = get_pno_ids_from_variants(df_pnos, df_upholstery_pno_prices, is_relation=False)
            df_upholstery_pnos_assigned.drop_duplicates(subset=['PNOID', 'Code', 'StartDate'], keep='last', inplace=True)
            df_upholsteries = self.get_table_df(self.config.get('AUTH', 'UPH'))
            df_upholstery = get_relation_ids(df_upholsteries, df_upholstery_pnos_assigned)
            self.upsert_data_from_df(df_upholstery, self.config.get('RELATIONS', 'UPH_Custom'), relation_columns, conditional_columns)

            df_package_pnos_assigned, df_pnos_unassigned = get_pno_ids_from_variants(df_pnos, df_package_pno_prices, is_relation=False)
            df_package_pnos_assigned.drop_duplicates(subset=['PNOID', 'StartDate'], keep='last', inplace=True)
            df_packages = self.get_table_df(self.config.get('AUTH', 'PKG'))
            df_package = get_relation_ids(df_packages, df_package_pnos_assigned)
            self.upsert_data_from_df(df_package, self.config.get('RELATIONS', 'PKG_Custom'), relation_columns, conditional_columns)
