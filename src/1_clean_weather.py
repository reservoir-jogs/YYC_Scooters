import logging
from pathlib import Path
import pandas as pd
import os

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

project_dir = Path().resolve().parents[0]

# Build weather file names
# Just included YYC Airport other codes in Calgary are: '3031094', '3031875'
station_id = ['3031092']
weather_name = ['en_climate_hourly_AB_' + x + '_' + y + '-2019_P1H.csv'
                for x in station_id
                for y in ['07', '08', '09']]

weather_files = [os.path.join(project_dir, 'data', 'raw', x) for x in weather_name]

logger.info(f"Reading files from: {weather_files}")
# Import all weather files
dfs = [pd.read_csv(f) for f in weather_files]
weather_data = pd.concat(dfs, ignore_index=True)

# Keep specific columns
columns_to_keep = ['Longitude (x)', 'Latitude (y)',
                   'Station Name', 'Climate ID',
                   'Date/Time',
                   'Year', 'Month', 'Day', 'Time',
                   'Temp (°C)', 'Dew Point Temp (°C)',
                   'Rel Hum (%)',
                   'Wind Dir (10s deg)', 'Wind Dir Flag', 'Wind Spd (km/h)',
                   'Visibility (km)', 'Stn Press (kPa)', 'Weather']
weather_data = weather_data.loc[:, columns_to_keep]

# Fill in NA values for Weather with the prior value (subsequent value for the first couple rows)
weather_data['Weather'] = weather_data['Weather'].fillna(method='ffill').fillna(method='bfill')

# Reduce the number of weather types to something manageable. Look for keywords of worst weather
weather_data.loc[weather_data.Weather.str.contains('Snow'), 'Weather'] = 'Snow'
weather_data.loc[weather_data.Weather.str.contains('Thunderstorms'), 'Weather'] = 'Thunderstorms'
weather_data.loc[weather_data.Weather.str.contains('Rain'), 'Weather'] = 'Rain'
weather_data.loc[weather_data.Weather.str.contains('Showers'), 'Weather'] = 'Rain'
weather_data.loc[weather_data.Weather.str.contains('Drizzle'), 'Weather'] = 'Rain'
weather_data.loc[weather_data.Weather.str.contains('Fog'), 'Weather'] = 'Fog'
weather_data.loc[weather_data.Weather.str.contains('Haze'), 'Weather'] = 'Fog'
weather_data.loc[weather_data.Weather.str.contains('Cloudy'), 'Weather'] = 'Cloudy'
weather_data.loc[weather_data.Weather.str.contains('Clear'), 'Weather'] = 'Clear'

# Save to interim
out_file = os.path.join(project_dir, 'data', 'interim', 'weather_data.csv')
logger.info('Saving to: ' + f"{out_file}")

weather_data.to_csv(out_file, index=False)
