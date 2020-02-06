import logging
import pandas as pd
from pathlib import Path
import datetime as dt
import os

# weather columns to keep for analysis
weather_cols = ['Temp (°C)', 'Wind Spd (km/h)', 'Weather', 'datetime']

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

project_dir = Path().resolve().parents[0]
scooter_name = os.path.join(project_dir, 'data', 'interim', 'scooter_data.csv')
weather_name = os.path.join(project_dir, 'data', 'interim', 'weather_data.csv')

logger.info(f"Reading file from: {scooter_name}")
scooterdf = pd.read_csv(scooter_name)

logger.info(f"Reading file from: {weather_name}")
weatherdf = pd.read_csv(weather_name)

# Calculate 'as the crow flies' distance
logger.info('Converting timestamps to datetime')
scooterdf['datetime'] = scooterdf.apply(lambda x: pd.to_datetime(x['start_date']) + dt.timedelta(hours=x['start_hour']), axis=1)
weatherdf['datetime'] = pd.to_datetime(weatherdf['Date/Time'])
weatherdf = weatherdf[weather_cols]

# Merge
logger.info('Merging scooter and weather data')
scooterdf = scooterdf.merge(weatherdf, on='datetime', how='left')

out_file = os.path.join(project_dir, 'data', 'final', 'all_data.csv')
logger.info("Saving to: " + f"{out_file}")
scooterdf.to_csv(out_file, index=False)
