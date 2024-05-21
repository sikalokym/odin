import logging
from src.database.db_operations import DBOperations

class SQLLoggingHandler(logging.Handler):
    def emit(self, record):
        # Get the country code from the log record; default to a specific value if not provided
        country_code = getattr(record, 'country_code', None)
        if country_code is None:
            # Handle the missing country code appropriately, e.g., default or raise an error
            print("Country code is missing in the log record")
            return
        # Get the current datetime
        rec_date = self.formatTime(record, self.datefmt)

        # Get the log level number
        levelno = record.levelno
        if levelno < 20:
            return

        # Get the message from the log record
        message = record.getMessage()

        try:
            with DBOperations.get_cursor() as cursor:
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


def setup_logger_config():
    # Create a handler that saves the logs to a file and saves them for 7 days
    new_handler = logging.handlers.TimedRotatingFileHandler('logs/app.log', when='D', interval=1, backupCount=7)
    new_handler.setLevel(logging.DEBUG)
    new_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(new_handler)

    # Create a handler that saves the logs to a database
    sql_handler = SQLLoggingHandler()
    sql_handler.setLevel(logging.DEBUG)
    logger.addHandler(sql_handler)


# Configure logging
logger = logging.getLogger(__name__)
