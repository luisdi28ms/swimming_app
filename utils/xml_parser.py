import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import os

# Path to your export.xml file (update this)
XML_PATH = 'data/export.xml'  # e.g., '/path/to/apple_health_export/export.xml'

# Output CSV files
WORKOUTS_CSV = 'data/swimming_workouts.csv'
DISTANCE_CSV = 'data/swimming_distance.csv'
STROKES_CSV = 'data/swimming_strokes.csv'

def parse_workouts(xml_path):
    """Parse <Workout> elements for swimming workouts."""
    workouts = []
    context = ET.iterparse(xml_path, events=('end',))
    for event, elem in context:
        if elem.tag == 'Workout' and elem.get('workoutActivityType') == 'HKWorkoutActivityTypeSwimming':
            workout = {
                'startDate': elem.get('startDate'),
                'endDate': elem.get('endDate'),
                'duration': elem.get('duration'),
                'durationUnit': elem.get('durationUnit'),
                'totalDistance': elem.get('totalDistance'),
                'totalDistanceUnit': elem.get('totalDistanceUnit'),
                'totalEnergyBurned': elem.get('totalEnergyBurned'),
                'totalEnergyBurnedUnit': elem.get('totalEnergyBurnedUnit'),
                'sourceName': elem.get('sourceName'),
                'sourceVersion': elem.get('sourceVersion'),
                'creationDate': elem.get('creationDate'),
            }
            workouts.append(workout)
        # Clear the element to save memory
        elem.clear()
    return pd.DataFrame(workouts)

def parse_records(xml_path, record_type):
    """Parse <Record> elements for specific types."""
    records = []
    context = ET.iterparse(xml_path, events=('end',))
    for event, elem in context:
        if elem.tag == 'Record' and elem.get('type') == record_type:
            record = {
                'startDate': elem.get('startDate'),
                'endDate': elem.get('endDate'),
                'value': elem.get('value'),
                'unit': elem.get('unit'),
                'sourceName': elem.get('sourceName'),
                'creationDate': elem.get('creationDate'),
            }
            records.append(record)
        elem.clear()
    return pd.DataFrame(records)

print("Parsing swimming workouts...")
workouts_df = parse_workouts(XML_PATH)

if not workouts_df.empty:
    # Convert dates to datetime for easier handling
    workouts_df['startDate'] = pd.to_datetime(workouts_df['startDate'])
    workouts_df['endDate'] = pd.to_datetime(workouts_df['endDate'])
    workouts_df['duration_min'] = pd.to_numeric(workouts_df['duration'])
    if 'totalDistance' in workouts_df.columns:
        workouts_df['totalDistance_m'] = pd.to_numeric(workouts_df['totalDistance'])
    
    workouts_df.to_csv(WORKOUTS_CSV, index=False)
    print(f"Saved {len(workouts_df)} swimming workouts to {WORKOUTS_CSV}")
else:
    print("No swimming workouts found.")

print("Parsing swimming distance records...")
distance_df = parse_records(XML_PATH, 'HKQuantityTypeIdentifierDistanceSwimming')
if not distance_df.empty:
    distance_df['startDate'] = pd.to_datetime(distance_df['startDate'])
    distance_df['value_m'] = pd.to_numeric(distance_df['value'])
    distance_df.to_csv(DISTANCE_CSV, index=False)
    print(f"Saved {len(distance_df)} distance records to {DISTANCE_CSV}")

print("Parsing swimming stroke count records...")
strokes_df = parse_records(XML_PATH, 'HKQuantityTypeIdentifierSwimmingStrokeCount')
if not strokes_df.empty:
    strokes_df['startDate'] = pd.to_datetime(strokes_df['startDate'])
    strokes_df['value'] = pd.to_numeric(strokes_df['value'])
    strokes_df.to_csv(STROKES_CSV, index=False)
    print(f"Saved {len(strokes_df)} stroke records to {STROKES_CSV}")

print("Done! Open the CSV files in Excel, Google Sheets, or Numbers.")
