from repositories.sql_alchemy import db

class RawSwimmingDistance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sourceName = db.Column(db.String(50))
    value = db.Column(db.Integer)
    unit = db.Column(db.String(50))
    startDate = db.Column(db.String(50))
    endDate = db.Column(db.String(50))
