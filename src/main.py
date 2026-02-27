from flask import Flask, render_template, Response, g, request
from controllers.data_collector import DataCollector
from controllers.data_analyzer import DataAnalyzer
from repositories.sql_alchemy import db
import os
from prometheus_client import Counter, Histogram, generate_latest
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///swimmers.db')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
with app.app_context():
    db.create_all()

data_collector = DataCollector()
analyzer = DataAnalyzer()

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency in seconds')
UPLOAD_COUNT = Counter('file_uploads_total', 'Total file uploads')
WORKOUT_ANALYSIS_COUNT = Counter('workout_analysis_total', 'Total workouts analyzed')

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - g.start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint or 'unknown', status=response.status_code).inc()
    REQUEST_LATENCY.observe(latency)
    return response

@app.route("/")
def main():
    return render_template("upload.html")

@app.route("/collect_user_data", methods=["POST"])
def collect_data():
    result = data_collector.collect_user_data()
    UPLOAD_COUNT.inc()
    return result

@app.route('/analyze_user_data')
def swimming_report():
    result = analyzer.render_swimming_report()
    WORKOUT_ANALYSIS_COUNT.inc()
    return result

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__": # pragma: no cover
    app.run(debug=True)

