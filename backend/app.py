from flask import Flask, render_template_string
from flask_cors import CORS
from src.database.db_connection import DatabaseConnection
from src.database.db_operations import DBOperations
from src.routes.ingest_routes import bp_ingest
from src.routes.db_reader_routes import bp_db_reader
from src.routes.db_writer_routes import bp_db_writer
from src.routes.exporter_routes import bp_exporter
from src.routes.settings_routes import bp_settings
import src.utils.scheduler as scheduler
from src.utils.sql_logging_handler import setup_logger_config
import time
import threading

app = Flask(__name__)
CORS(app)

app.register_blueprint(bp_settings)
app.register_blueprint(bp_ingest)
app.register_blueprint(bp_db_reader)
app.register_blueprint(bp_db_writer)
app.register_blueprint(bp_exporter)

# Template string for rendering the welcome page
WELCOME_PAGE_TEMPLATE = """
<!doctype html>
<html>
<head><title>Welcome to PMT</title></head>
<body>
    <h1>Welcome to My Flask App</h1>
    <p>Here are all the possible paths:</p>
    <ul>
        {% for rule in rules %}
        <li>{{ rule }}</li>
        {% endfor %}
    </ul> 
</body>
</html>
"""

last_request_time = time.time()  # Global variable to store the last request timestamp
open_db_connection = False  # Global variable to store the status of the database connection

def close_db_connection_after_inactivity():
    global last_request_time
    global open_db_connection
    while open_db_connection:
        current_time = time.time()
        if current_time - last_request_time >= 60:
            DatabaseConnection.close_connection()
            open_db_connection = False
        time.sleep(60)

@app.before_request
def before_request():
    global open_db_connection
    if not open_db_connection:
        DBOperations.create_instance()

@app.after_request
def after_request(response):
    global last_request_time
    last_request_time = time.time()
    global open_db_connection
    if not open_db_connection:
        open_db_connection = True
        threading.Thread(target=close_db_connection_after_inactivity, daemon=True).start()
    return response

@app.route('/', methods=['GET'])
def welcome():
    rules = [str(rule) for rule in app.url_map.iter_rules() if str(rule) != '/static/<path:filename>']
    return render_template_string(WELCOME_PAGE_TEMPLATE, rules=rules)

if __name__ == "__main__":
    scheduler.cpam_scheduler.start()
    setup_logger_config()
    app.run(debug=True, port=5000)
