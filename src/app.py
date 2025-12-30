#!/usr/bin/env python3

from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def main():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Echo App</title>
        <style>
            body { font-family: sans-serif; margin: 40px; text-align: center; }
            h1 { color: #333; }
            input[type=text] { padding: 8px; width: 300px; font-size: 16px; }
            input[type=submit] { padding: 8px 16px; font-size: 16px; }
        </style>
    </head>
    <body>
        <h1>Echo Your Input</h1>
        <form action="/echo_user_input" method="POST">
            <input name="user_input" placeholder="Type something...">
            <input type="submit" value="Submit!">
        </form>
    </body>
    </html>
    '''

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Echo App</title>
        <style>
            body { font-family: sans-serif; margin: 40px; text-align: center; }
            h1 { color: #333; }
            input[type=text] { padding: 8px; width: 300px; font-size: 16px; }
            input[type=submit] { padding: 8px 16px; font-size: 16px; }
            .result { margin-top: 30px; font-size: 20px; }
        </style>
    </head>
    <body>
        <h1>Echo Your Input</h1>
        <form action="/echo_user_input" method="POST">
            <input name="user_input" value="''' + input_text + '''" placeholder="Type something...">
            <input type="submit" value="Submit!">
        </form>
        <div class="result">You entered: ''' + input_text + '''</div>
        <p><a href="/">← Start over</a></p>
    </body>
    </html>
    '''
