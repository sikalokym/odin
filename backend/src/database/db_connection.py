import os
import pyodbc
import logging

class DatabaseConnection:
    logger = logging.getLogger(__name__)
    connection = None

    @classmethod
    def close_connection(self):
        self.logger.debug('Closing database connection')
        try:
            if self.connection:
                self.connection.close()
                self.logger.debug('Database connection closed')
        except pyodbc.Error as e:
            self.logger.error('Failed to close database connection', exc_info=True)
            raise e

    @classmethod
    def get_db_connection(self):
        self.logger.debug('Starting database connection')
        try:
            if self.connection is None or self.connection.closed:
                connection_string = os.environ.get('DB_CONNECTION_STRING')
                self.connection = pyodbc.connect(connection_string)
            return self.connection
        except pyodbc.Error as e:
            self.logger.error('Failed to start database connection', exc_info=True)
            raise e
        
    @classmethod
    def create_connection(self, connection_string):
        self.logger.debug('Starting database connection')
        try:
            if self.connection is None or self.connection.closed:
                self.connection = pyodbc.connect(connection_string)
            return self.connection
        except pyodbc.Error as e:
            self.logger.error('Failed to start database connection', exc_info=True)
            raise e
