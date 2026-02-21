from flask import render_template
from sqlalchemy import func
from models.raw_swimming_distance import RawSwimmingDistance
from repositories.sql_alchemy import db


class DataAnalyzer:
    """Analyzes swimming distance data and renders HTML reports."""

    def get_all_records(self):
        """Fetch all swimming distance records."""
        return RawSwimmingDistance.query.all()

    def get_total_distance(self):
        """Calculate total swimming distance in meters."""
        result = db.session.query(func.sum(RawSwimmingDistance.value)).scalar()
        return result or 0

    def get_average_distance(self):
        """Calculate average swimming distance per session."""
        result = db.session.query(func.avg(RawSwimmingDistance.value)).scalar()
        return result or 0

    def get_total_sessions(self):
        """Get total number of swimming sessions."""
        return RawSwimmingDistance.query.count()

    def get_records_by_source(self, source_name):
        """Fetch records filtered by source name."""
        return RawSwimmingDistance.query.filter_by(sourceName=source_name).all()

    def render_swimming_report(self):
        """Render the complete swimming distance HTML report."""
        records = self.get_all_records()
        total_distance = self.get_total_distance()
        avg_distance = self.get_average_distance()
        total_sessions = self.get_total_sessions()

        return render_template(
            "analyzed_data.html",
            records=records,
            total_distance=total_distance,
            avg_distance=avg_distance,
            total_sessions=total_sessions
        )     
