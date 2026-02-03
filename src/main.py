#!/usr/bin/env python3
from flask import Flask, render_template, request
from models.data_collector import process_upload

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("upload.html")

@app.route("/collect_user_data", methods=["POST"])
def collect_user_data():
    file = request.files.get("user_input")

    if not file or file.filename == '':
        return "<h1>Error: No file selected!</h1>", 400

    try:
        # Delegate data work to the Model
        data = process_upload(file)
        # Delegate display work to the View
        return render_template("results.html", head=data['head'], tail=data['tail'])
    except Exception as e:
        return f"<h1>Error processing file:</h1> <p>{str(e)}</p>", 500

if __name__ == "__main__":
    app.run(debug=True)
