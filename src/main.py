#!/usr/bin/env python3
from flask import Flask, render_template
from controllers.data_collector import DataCollector
from controllers.data_analyzer import DataAnalyzer
from repositories.sql_alchemy import db
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///swimmers.db')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/home/deployer/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
with app.app_context():
    db.create_all()

data_collector = DataCollector()
analyzer = DataAnalyzer()

@app.route("/")
def main():
    return render_template("upload.html")

@app.route("/collect_user_data", methods=["POST"])
def collect_data():
    return data_collector.collect_user_data()

@app.route('/analyze_user_data')
def swimming_report():
    return analyzer.render_swimming_report()

if __name__ == "__main__":
    app.run(debug=True)
