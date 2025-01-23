import logging.handlers
import logging
import os

from src.database.db_operations import DBOperations

# @author Hassan Wahba

class DispatchingFormatter:
    """Dispatch formatter for logger and it's sub logger."""
    def __init__(self, formatters, default_formatter):
        self._formatters = formatters
        self._default_formatter = default_formatter

    def format(self, record):
        # Search from record's logger up to it's parents:
        logger = logging.getLogger(record.name)
        while logger:
            # Check if suitable formatter for current logger exists:
            if logger.name in self._formatters:
                formatter = self._formatters[logger.name]
                break
            else:
                logger = logger.parent
        else:
            # If no formatter found, just use default:
            formatter = self._default_formatter
        return formatter.format(record)

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

if not os.path.exists('logs'):
    os.makedirs('logs')
fh_handler = logging.handlers.TimedRotatingFileHandler('logs/app.log', when='D', interval=1, backupCount=7)
fh_handler.setLevel(logging.DEBUG)
fh_handler.setFormatter(DispatchingFormatter(
        {
            'cpam-processing': logging.Formatter('%(asctime)s - %(levelname)s - %(country)s - %(year)s - %(message)s'),
            'cpam-processing-cartype': logging.Formatter('%(asctime)s - %(levelname)s - %(country)s - %(year)s - %(cartype)s - %(message)s')
        },
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'),
    )
)
fh_handler.setLevel(logging.DEBUG)

logging.getLogger().addHandler(fh_handler)

# new_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(country_code)s - %(message)s'))

# logger.addHandler(new_handler)

# Create a handler that saves the logs to a databases
# sql_handler = SQLLoggingHandler()
# sql_handler.setLevel(logging.DEBUG)
# logger.addHandler(sql_handler)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

cpam_processing_logger = logging.getLogger('cpam-processing')
cpam_processing_logger.setLevel(logging.INFO)

cpam_processing_cartype_logger = logging.getLogger('cpam-processing-cartype')
cpam_processing_cartype_logger.setLevel(logging.INFO)


# logger = setup_logger_config(logger)
