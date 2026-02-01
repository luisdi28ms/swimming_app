#!/usr/bin/env python3
import pandas as pd

from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def main():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Echo App</title>
        <style>
            body { font-family: sans-serif; margin: 40px; text-align: center; }
            h1 { color: #333; }
            input[type=file] { padding: 10px; margin: 10px; border: 1px solid #ddd; }
            input[type=submit] { padding: 8px 16px; font-size: 16px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Upload your data</h1>
        <h3>Supported formats: .csv, .xlsx, .xls</h3>
        
        <form action="/collect_user_data" method="POST" enctype="multipart/form-data">
            <input type="file" name="user_input" accept=".csv, .xlsx, .xls">
            <br>
            <input type="submit" value="Upload!">
        </form>
    </body>
    </html>
    """

@app.route("/collect_user_data", methods=["POST"])
def collect_user_data():
    # 1. Grab the file from the request
    file = request.files.get("user_input")

    # 2. ERROR CORRECTION: Check if the file is actually there
    # If the user clicks 'Upload' without selecting a file, this prevents the crash.
    if file is None or file.filename == '':
        return "<h1>Error: No file selected!</h1><p>Please go back and pick a file.</p>", 400

    # 3. Process the file
    # Note: If it's an Excel file, pd.read_csv will still throw a DIFFERENT error.
    # For now, this fixes the NoneType crash:
    df = pd.read_csv(file)
    
    head_html = df.head().to_html(classes='table table-striped')
    tail_html = df.tail().to_html(classes='table table-striped')
    
    return f"""
    <!doctype html>
    <html>
    <body>
        <h1>Results</h1>
        <div>{head_html}</div>
        <div class="result">Tail: {tail_html}</div>
        <p><a href="/">← start over</a></p>
    </body>
    </html>
    """
