from flask import render_template
from models.raw_swimming_distance import RawSwimmingDistance
from models.swim_stats import SwimStats
import pandas as pd

class DataAnalyzer:
    """Analyzes swimming distance data and renders HTML reports."""

    def _build_display_table(self):
        """Builds the grouped/cleaned dataframe for display purposes."""
        records = RawSwimmingDistance.query.all()
        df = pd.DataFrame([r.__dict__ for r in records])
        df["startDate"] = pd.to_datetime(df["startDate"])
        df["endDate"] = pd.to_datetime(df["endDate"])

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
        df["Duration"] = (df["End Date"] - df["Start Date"]).dt.total_seconds() / 60
        return df

    def render_swimming_report(self):
        """Render the complete swimming distance HTML report."""
        stats = SwimStats.query.first()

        if not stats:
            return render_template("analyzed_data.html", no_data=True)

        df = self._build_display_table()

        return render_template(
            "analyzed_data.html",
            record_list=df.to_html(classes='table table-striped', index=False),
            avg_distance=stats.avg_distance,
            avg_session=stats.avg_session,
            longest_distance=stats.longest_distance,
            longest_session=stats.longest_session,
            total_distance=stats.total_distance,
            total_sessions=stats.total_sessions
        )
