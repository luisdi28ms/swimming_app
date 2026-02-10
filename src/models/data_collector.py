import pandas as pd
from flask import render_template, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DataCollector:

    def collect_user_data(self):
        file = request.files.get("user_input")

        if not file or file.filename == '':
            return "<h1>Error: No file selected!</h1>", 400

        # TODO: Add file extension validation
        try:
            # Delegate data work to the Model
            data = self._process_upload(file)
            # Delegate display work to the View
            return render_template("results.html", head=data['head'], tail=data['tail'])
        except Exception as e:
            return f"<h1>Error processing file:</h1> <p>{str(e)}</p>", 500


    def _process_upload(self, file):
        """Handles different file types and returns head/tail HTML."""
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            # Requires 'openpyxl' installed for .xlsx
            df = pd.read_excel(file)
        if file.filename.endswith('swimming_workouts.csv'):
            df = df.drop_duplicates("startDate")
            df = df[['startDate', 'endDate', 'totalDistance',
                   'duration_min'
                     ]]
            df.to_sql('swimming_workout', con=db.engine, if_exists='append', index=False)

        return {
            "head": df.head().to_html(classes='table table-striped'),
            "tail": df.tail().to_html(classes='table table-striped')
        }

class SwimmingWorkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    startDate = db.Column(db.String(50))
    endDate = db.Column(db.String(50))
    totalDistance = db.Column(db.Float)
    duration_min = db.Column(db.Float)
