from repositories.sql_alchemy import db
import datetime as dt

class SwimStats(db.Model):
    __tablename__ = 'swim_stats'
    id = db.Column(db.Integer, primary_key=True)
    avg_distance = db.Column(db.Float)
    avg_session = db.Column(db.Float)
    longest_distance = db.Column(db.Float)
    longest_session = db.Column(db.Float)
    total_distance = db.Column(db.Float)
    total_sessions = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=dt.datetime.now(dt.timezone.utc))
