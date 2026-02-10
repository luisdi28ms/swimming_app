#!/usr/bin/env python3
from flask import Flask, render_template
from models.data_collector import DataCollector, db
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///swimmers.db')
db.init_app(app)
with app.app_context():
    db.create_all()

data_collector = DataCollector()

@app.route("/")
def main():
    return render_template("upload.html")

@app.route("/collect_user_data", methods=["POST"])
def collect_data():
    return data_collector.collect_user_data()

if __name__ == "__main__":
    app.run(debug=True)
