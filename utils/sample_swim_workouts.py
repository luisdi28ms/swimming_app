import pandas as pd

df = pd.read_csv("data/swimming_workouts.csv")
df = df.drop_duplicates("startDate")
df = df[['startDate', 'endDate', 'totalDistance',
       'totalDistanceUnit', 'totalEnergyBurned', 'totalEnergyBurnedUnit',
       'sourceName', 'sourceVersion', 'creationDate', 'duration_min',
       'totalDistance_m']]
df = df[df["totalDistance"].isna() == False].copy()
print(df)
print(df.columns)
print(df.size)


df = pd.read_csv("data/swimming_distance.csv")
print(df)
