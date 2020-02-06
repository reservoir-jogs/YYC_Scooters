import logging
import pandas as pd
from pathlib import Path
import geopy.distance
import math
import os

# Some constants
km_per_m = 0.001
s_per_hr = 60*60
cdn_holidays = {'2019/07/01': 'Canada Day', '2019/08/05': 'Heritage Day', '2019/09/02': 'Labour Day'}


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

project_dir = Path().resolve().parents[0]

file_name = os.path.join(project_dir, 'data', 'raw', 'Shared_Mobility_Pilot_Trips.csv')
logger.info(f"Reading file from: {file_name}")
df = pd.read_csv(file_name)

# Calculate 'as the crow flies' distance
logger.info('Calculating distances')
df['a_dist'] = df.apply(lambda x: geopy.distance.distance((x['starty'], x['startx']),
                                                          (x['endy'], x['endx'])).m, axis=1)

# max length of 10,000m2 regular hexagon A=(3*sqrt(3)s^2)/2
cell_length = math.sqrt(2*10000/(3*math.sqrt(3)))

# Put min of total distance traveled or in one cell length as distance traveled if finished in same block
df['a_dist'] = df.apply(lambda x: min(x['trip_distance'],
                                      cell_length) if x['a_dist'] < cell_length else x['a_dist'], axis=1)

# Calculate other fields
logger.info('Calculating other fields')
df['travel_efficiency'] = df['a_dist']/df['trip_distance']
df['speed'] = (df['trip_distance']*km_per_m*s_per_hr)/(df['trip_duration'])
df['a_speed'] = (df['a_dist']*km_per_m*s_per_hr)/(df['trip_duration'])

# Drop unused columns
logger.info("Dropping unused columns")
col_to_drop = ['start_grid_count', 'end_grid_count',
               'Hexbins', 'Calgary Communities', 'startpoint', 'endpoint']
df.drop(col_to_drop, inplace=True, axis=1)

logger.info("Cleaning & creating days of the week variables")
df['start_day_of_week'] = df['start_day_of_week'].apply(lambda x: x[0])

# Create 'is_weekend' variable
df['is_weekend'] = 0
df.loc[(df['start_day'] == "Sunday") | (df['start_day'] == "Saturday"), 'is_weekend'] = 1

# Create 'is_holiday' variable
df['is_holiday'] = 0
df.loc[df['start_date'].apply(lambda x: x in cdn_holidays), 'is_holiday'] = 1

out_file = os.path.join(project_dir, 'data', 'interim', 'scooter_data.csv')
logger.info('Saving to: ' + f"{out_file}")
df.to_csv(out_file, index=False)
