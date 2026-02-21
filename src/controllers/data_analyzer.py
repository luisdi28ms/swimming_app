from flask import render_template
from sqlalchemy import func
from models.raw_swimming_distance import RawSwimmingDistance
from repositories.sql_alchemy import db
import pandas as pd
import datetime as dt



class DataAnalyzer:
    """Analyzes swimming distance data and renders HTML reports."""

    def get_clean_records(self):
        """Fetch all swimming distance records."""
        df = pd.DataFrame([r.__dict__ for r in RawSwimmingDistance.query.all()])
        df["startDate"] = pd.to_datetime(df["startDate"])
        df["endDate"] = pd.to_datetime(df["endDate"])

        # Clean Source Name
        cond = df["sourceName"].str.contains("Apple")
        df.loc[cond, "sourceName"] = "Apple Watch"

        cond = df["sourceName"].str.contains("Connect")
        df.loc[cond, "sourceName"] = "Garmin"


        df = df.groupby(df["startDate"].dt.date).agg(
        **{
            "Source Name": ("sourceName", "first"),
            "Value": ("value", "sum"),
            "Start Date": ("startDate", "min"),
            "End Date": ("endDate", "max"),
        }
    )
        df["Duration"] = (df["End Date"] - df["Start Date"]).dt.total_seconds()/60
        return df

    def render_swimming_report(self):
        """Render the complete swimming distance HTML report."""
        df = self.get_clean_records()
        avg_distance = df["Value"].mean()
        avg_session = df["Duration"].mean() if len(df) > 0 else 0
        longest_distance = df["Value"].max()
        longest_session = df["Duration"].max()
        total_distance = df["Value"].sum()
        total_sessions = len(df["Value"])

        return render_template(
            "analyzed_data.html",
            record_list=df.to_html(classes='table table-striped', index=False),
            avg_distance=avg_distance,
            avg_session=avg_session,
            longest_distance=longest_distance,
            longest_session=longest_session,
            total_distance=total_distance,
            total_sessions=total_sessions

        )     
