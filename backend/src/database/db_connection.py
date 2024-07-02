import os
import pyodbc
import logging
from time import sleep

class DatabaseConnection:
    logger = logging.getLogger(__name__)
    connection = None

    @classmethod
    def close_connection(self):
        self.logger.debug('Closing database connection')
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
            self.connection = None
            self.logger.debug('Database connection closed')
        except pyodbc.Error as e:
            self.logger.error('Failed to close database connection', exc_info=True)
            raise e

    @classmethod
    def get_db_connection(self, test=False, max_attempts=3):
        self.logger.debug('Starting database connection')
        for attempt in range(max_attempts):
            try:
                if self.connection is None or self.connection.closed:
                    connection_string = os.environ.get('TEST_DB_CONNECTION_STRING') if test else os.environ.get('DB_CONNECTION_STRING')
                    self.connection = pyodbc.connect(connection_string)
                return self.connection
            except pyodbc.Error as e:
                self.logger.error(f'Failed to start database connection, attempt {attempt + 1}', exc_info=True)
                if attempt + 1 == max_attempts:
                    raise e
                else:
                    sleep(1)
    
    @classmethod
    def reconnect(self):
        self.logger.debug('Reconnecting to database')
        self.close_connection()
        self.logger.debug('Reconnected to database')
        return self.get_db_connection()
