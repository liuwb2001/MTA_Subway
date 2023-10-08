import folium
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# Load the data
file_path = 'MTA_100000.csv'
mta_data = pd.read_csv(file_path)

# Display basic info and the first few rows of the data
mta_data.info(), mta_data.head()

# Create a base map
map_nyc_3 = folium.Map(location=[40.730610, -73.935242], zoom_start=11)

# Data Preprocessing

# Extract unique stations and their properties (latitude, longitude, and routes)
stations = mta_data[['station_complex', 'latitude', 'longitude', 'routes']].drop_duplicates()

# Analyzing routes: Extracting all unique routes to assign colors later
unique_routes = set()
stations['routes'].apply(lambda x: unique_routes.update(x.split(',')))

# Extracting total ridership per station
total_ridership = mta_data.groupby('station_complex')['ridership'].sum().reset_index()

# Merging the stations info with total ridership
stations_info = pd.merge(stations, total_ridership, how='left', on='station_complex')

# Display basic info and the first few rows of the preprocessed data
stations_info.info(), stations_info.head(), unique_routes


# Calculate the percentile-based mapping of ridership to a range of 1-20
percentiles = stations_info['ridership'].rank(pct=True)
min_percentile = percentiles.min()
max_percentile = percentiles.max()
stations_info['mapped_ridership'] = 1 + 19 * (percentiles - min_percentile) / (max_percentile - min_percentile)

# Define the color gradient
# Define the custom colormap
colors = [(0.0, 'blue'), (0.2, 'blue'), (0.5, 'lime'), (0.8, 'red'), (1.0, 'red')]
custom_cmap = LinearSegmentedColormap.from_list("custom", colors)

# First, let's categorize the ridership into 20 buckets based on percentiles
stations_info['ridership_rank'] = pd.qcut(stations_info['ridership'], q=[0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1], labels=False)

route_colors = plt.cm.viridis(np.linspace(0, 1, len(unique_routes)))
route_color_map = {route: f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
                   for route, (r, g, b, a) in zip(unique_routes, route_colors)}


for idx, row in stations_info.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=route_color_map[row['routes'][0]],
        fill=True,
        fill_color=route_color_map[row['routes'][0]],
        popup=f"Station: {row['station_complex']}<br>Routes: {row['routes']}<br>Ridership: {row['ridership']}",
    ).add_to(map_nyc_3)

# Now, we iterate through routes and draw lines between stations
stations_info['ridership_rank'] = pd.qcut(stations_info['ridership'], q=10, labels=False)

# Now, we iterate through routes and draw lines between stations
for route in unique_routes:
    if route:  # skip empty route
        route_stations = stations_info[stations_info['routes'].apply(lambda x: route in x.split(','))].copy()
        route_stations.sort_values(by='latitude', inplace=True)
        for idx in range(1, len(route_stations)):
            start_station = route_stations.iloc[idx-1]
            end_station = route_stations.iloc[idx]
            # Draw a line between the stations, colored based on average ridership rank (higher rank means higher ridership)
            avg_ridership_rank = (start_station['ridership_rank'] + end_station['ridership_rank']) / 2
            line_color = plt.cm.turbo(avg_ridership_rank / 9)  # Normalize to 0-1
            line_color_hex = f'#{int(line_color[0]*255):02x}{int(line_color[1]*255):02x}{int(line_color[2]*255):02x}'
            folium.PolyLine([(start_station['latitude'], start_station['longitude']),
                             (end_station['latitude'], end_station['longitude'])],
                            color=line_color_hex).add_to(map_nyc_3)

# Save the map as an HTML file
map_nyc_3.save("nyc_subway_map_line.html")

