import pika
import os
import json
import pandas as pd
from main import app, db
from models.raw_swimming_distance import RawSwimmingDistance
from models.swim_stats import SwimStats
import datetime as dt

def compute_stats(df):
    """Same logic as your get_clean_records, runs after raw data is stored."""
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

def process_file(filepath, filename):
    raw_df = pd.read_csv(filepath)

    if filename.endswith('swimming_distance.csv'):
        raw_df = raw_df[raw_df["value"] > 0].copy()
        columns = ["sourceName", "value", "unit", "startDate", "endDate"]
        raw_df = raw_df.loc[:, columns].copy()
        raw_df.index.name = 'id'
        raw_df.reset_index(inplace=True)

        with app.app_context():
            raw_df.to_sql('raw_swimming_distance', con=db.engine, if_exists='append', index=False)

            all_records = pd.DataFrame([r.__dict__ for r in RawSwimmingDistance.query.all()])
            df = compute_stats(all_records)

            stats = SwimStats.query.first()
            if not stats:
                stats = SwimStats()
                db.session.add(stats)

            stats.avg_distance = df["Value"].mean()
            stats.avg_session = df["Duration"].mean() if len(df) > 0 else 0
            stats.longest_distance = df["Value"].max()
            stats.longest_session = df["Duration"].max()
            stats.total_distance = df["Value"].sum()
            stats.total_sessions = len(df)
            stats.updated_at = dt.datetime.now(dt.timezone.utc)
            db.session.commit()

            print(f"Processed {len(raw_df)} raw rows, stats updated.")

def handle_message(ch, method, properties, body):
    data = json.loads(body)
    try:
        process_file(data['filepath'], data['filename'])
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

if __name__ == '__main__':
    url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
    connection = pika.BlockingConnection(pika.URLParameters(url))
    channel = connection.channel()
    channel.queue_declare(queue='csv_processing', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='csv_processing', on_message_callback=handle_message)
    print('Worker ready...')
    channel.start_consuming()
