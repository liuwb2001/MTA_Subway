import folium
from folium.plugins import HeatMap
import pandas as pd
from tqdm import tqdm

# Filtering data for the first day
mta_data = pd.read_csv("MTA_Subway_Hourly_Ridership__Beginning_February_2022.csv")
mta_data['transit_timestamp'] = pd.to_datetime(mta_data['transit_timestamp'], errors='coerce')
data_day = mta_data[mta_data['transit_timestamp'].dt.date == pd.to_datetime('2022-02-01').date()]

# Grouping by location and summing the ridership
grouped_day = data_day.groupby(['latitude', 'longitude'])['ridership'].sum().reset_index()

# Creating a base map
m = folium.Map(location=[40.730610, -73.935242], # Approximate central point
               zoom_start=11, control_scale=True)

# Creating a HeatMap
heat_data = []

# Loop through each row in the DataFrame with a progress bar
for index, row in tqdm(grouped_day.iterrows(), total=grouped_day.shape[0]):
    # Extract the latitude, longitude, and ridership from the row
    latitude = row['latitude']
    longitude = row['longitude']
    ridership = row['ridership']

    # Append the data to the heat_data list
    heat_data.append([latitude, longitude, ridership])

HeatMap(heat_data, radius=20).add_to(m)

# Save the map
map_path = 'nyc_heatmap_example.html'
m.save(map_path)

# Display the path for user download
map_path
