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
                    INSERT INTO Log (CountryCode, LogDate, LogType, LogMessage)
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

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = SQLLoggingHandler()
logger.addHandler(handler)

# Create a handler that saves the logs to a file and saves them for 7 days
# new_handler = logging.handlers.TimedRotatingFileHandler('logs/app.log', when='D', interval=1, backupCount=7)
# handler = logging.handlers.TimedRotatingFileHandler('logs/app.log', when='D', interval=1, backupCount=7)
