import pandas as pd
from flask import render_template, request
from models.raw_swimming_distance import RawSwimmingDistance
from repositories.sql_alchemy import db


class DataCollector:

    def collect_user_data(self):
        file = request.files.get("user_input")

        if not file or file.filename == '':
            return "<h1>Error: No file selected!</h1>", 400

        # TODO: Add file extension validation
        try:
            data = self._process_upload(file)
            return render_template("uploaded_data.html", head=data['head'], tail=data['tail'], row_count=data['row_count'])
        except Exception as e:
            return f"<h1>Error processing file:</h1> <p>{str(e)}</p>", 500


    def _process_upload(self, file):
        """Handles different file types and returns head/tail HTML."""
        df = pd.read_csv(file)
        if file.filename.endswith('swimming_distance.csv'):
            condition = df["value"] > 0
            df = df[condition].copy()
            columns = ["sourceName", "value", "unit", "startDate", "endDate"]
            df = df.loc[:,columns].copy()
            df.index.name = 'id'
            df.reset_index(inplace=True)
            df.to_sql('raw_swimming_distance', con=db.engine, if_exists='append', index=False)


        return {
            "head": df.head().to_html(classes='table table-striped', index=False),
            "tail": df.tail().to_html(classes='table table-striped', index=False),
            "row_count": RawSwimmingDistance.query.count()

        }


