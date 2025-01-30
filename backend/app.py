from flask import Flask, render_template_string
from threading import Thread, Lock
from flask_cors import CORS
import time

from src.database.db_connection import DatabaseConnection
from src.database.db_operations import DBOperations
from src.routes.db_reader_routes import bp_db_reader
from src.routes.db_writer_routes import bp_db_writer
from src.routes.exporter_routes import bp_exporter
from src.routes.settings_routes import bp_settings
from src.routes.scheduler_routes import bp_scheduler
from src.utils.sql_logging_handler import logger
from src.routes.ingest_routes import bp_ingest
from src.utils.scheduler import cpam_scheduler


# @author Hassan Wahba

cpam_scheduler.start()

app = Flask(__name__)
CORS(app)

app.register_blueprint(bp_settings)
app.register_blueprint(bp_ingest)
app.register_blueprint(bp_db_reader)
app.register_blueprint(bp_db_writer)
app.register_blueprint(bp_exporter)
app.register_blueprint(bp_scheduler)


# Template string for rendering the welcome page
WELCOME_PAGE_TEMPLATE = """
<!doctype html>
<html>
<head><title>PMT API Endpoints</title></head>
<body>
    <h1>The Endpoints for ODIN</h1>
    <p>Here are all the possible paths:</p>
    <ul>
        {% for rule in rules %}
        <li>{{ rule }}</li>
        {% endfor %}
    </ul> 
</body>
</html>
"""

last_request_time = time.time()
open_reqs = 0
reqs_lock = Lock()

def close_db_connection_after_inactivity():
    global last_request_time, open_reqs
    while True:
        with reqs_lock:
            if open_reqs > 0:
                break
            elif time.time() - last_request_time >= 60:
                DatabaseConnection.close_connection()
                break
            
@app.before_request
def before_request():
    global open_reqs
    with reqs_lock:
        if open_reqs == 0:
            DBOperations.create_instance(logger=logger)
        open_reqs += 1

@app.teardown_request
def teardown_request(exception):
    global last_request_time, open_reqs
    last_request_time = time.time()
    with reqs_lock:
        open_reqs -= 1
        if open_reqs == 0:
            Thread(target=close_db_connection_after_inactivity).start()

@app.route('/', methods=['GET'])
def welcome():
    rules = [str(rule) for rule in app.url_map.iter_rules() if str(rule) != '/static/<path:filename>']
    return render_template_string(WELCOME_PAGE_TEMPLATE, rules=rules)

if __name__ == "__main__":
    app.run(debug=False, port=5000, use_reloader=False)
