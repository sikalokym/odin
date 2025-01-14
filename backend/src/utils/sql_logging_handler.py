import logging.handlers
import logging
import os

from src.database.db_operations import DBOperations

# @author Hassan Wahba

class SQLLoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.formatter = logging.Formatter()
    
    def emit(self, record):
        # Get the country code from the log record; default to a specific value if not provided
        country_code = getattr(record, 'country_code', None)
        if country_code is None:
            return
        # Get the current datetime
        rec_date = self.formatter.formatTime(record, self.formatter.default_time_format)
        
        # Get the log level number
        levelno = record.levelno
        if levelno < 10:
            return

        # Get the message from the log record
        message = record.getMessage()

        try:
            with DBOperations.instance.get_cursor() as cursor:
                insert_query = '''
                    INSERT INTO DataQualityLog (CountryCode, LogDate, LogType, LogMessage)
                    VALUES (?, ?, ?, ?)
                '''
                cursor.execute(insert_query, (
                    country_code,
                    rec_date,
                    record.levelname,
                    message
                ))
        except Exception as e:
            print(f"Failed to log message to database: {e}")

def setup_logger_config(logger):
    # Create a handler that saves the logs to a file and saves them for 7 days

    if not os.path.exists('logs'):
        os.makedirs('logs')
    new_handler = logging.handlers.TimedRotatingFileHandler('logs/app.log', when='D', interval=1, backupCount=7)
    new_handler.setLevel(logging.DEBUG)
    new_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(new_handler)

    # Create a handler that saves the logs to a database
    sql_handler = SQLLoggingHandler()
    sql_handler.setLevel(logging.DEBUG)
    logger.addHandler(sql_handler)
    return logger

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger = setup_logger_config(logger)
