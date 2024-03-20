import logging
from flask import Flask, render_template_string
from flask_cors import CORS
from src.database.db_operations import DBOperations
from src.routes.ingest_routes import bp_ingest
from src.routes.db_reader_routes import bp_db_reader
from src.routes.db_writer_routes import bp_db_writer
from src.routes.exporter_routes import bp_exporter
from src.routes.settings_routes import bp_settings


app = Flask(__name__)
CORS(app)

# Setup logging
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)

app.register_blueprint(bp_settings)
app.register_blueprint(bp_ingest)
app.register_blueprint(bp_db_reader)
app.register_blueprint(bp_db_writer)
app.register_blueprint(bp_exporter)

DBOperations.create_instance()

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

@app.route('/', methods=['GET'])
def welcome():
    rules = [str(rule) for rule in app.url_map.iter_rules() if str(rule) != '/static/<path:filename>']
    return render_template_string(WELCOME_PAGE_TEMPLATE, rules=rules)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, port=5000)
