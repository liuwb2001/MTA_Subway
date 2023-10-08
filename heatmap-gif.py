import os
import pandas as pd
import folium
from folium.plugins import HeatMap
import imageio
from selenium import webdriver
from time import sleep

# Load the data
data_path = 'MTA_Subway_Hourly_Ridership__Beginning_February_2022.csv'  # Update path to your data
mta_data = pd.read_csv(data_path)
# mta_data['transit_timestamp'] = pd.to_datetime(mta_data['transit_timestamp'], errors='coerce')
# mta_data['day_of_week'] = mta_data['transit_timestamp'].dt.day_name()
# mta_data['hour'] = mta_data['transit_timestamp'].dt.hour


# Define a function to create and save a heatmap
def create_heatmap(data, day, hour, img_path):
    m = folium.Map(location=[40.730610, -73.935242], zoom_start=11, control_scale=True)
    heat_data = [[row['latitude'], row['longitude'], row['ridership']] for index, row in data.iterrows()]
    HeatMap(heat_data, radius=20).add_to(m)

    title_html = f'''
        <h3 align="center" style="font-size:16px"><b>{day} {hour}:00</b></h3>
        '''
    m.get_root().html.add_child(folium.Element(title_html))

    m.save(img_path)
    return img_path


# Define a function to take a screenshot of a webpage
def get_screenshot(url, img_path):
    driver = webdriver.Firefox()  # Update path to geckodriver
    driver.get(url)
    sleep(3)  # Wait for the page to fully load
    driver.save_screenshot(img_path)
    driver.quit()
    return img_path


# Creating a directory to save the images and gif
img_dir = 'heatmap_imgs/'
os.makedirs(img_dir, exist_ok=True)

# Generating heatmaps for each hour of each day of the week
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
img_paths = []

for day in days_of_week:
    for hour in range(24):
        html_path = f"{img_dir}{day}_{hour}.html"
        png_path = f"{img_dir}{day}_{hour}.png"

        # data_hour = mta_data[(mta_data['day_of_week'] == day) & (mta_data['hour'] == hour)]
        # grouped_hour = data_hour.groupby(['latitude', 'longitude'])['ridership'].sum().reset_index()

        # Create heatmap and save as html
        # create_heatmap(grouped_hour, day, hour, html_path)
        # Convert the html to png
        #get_screenshot('file://' + os.path.abspath(html_path), png_path)
        img_paths.append(png_path)

# Create a GIF
gif_path = "heatmap_animation.gif"
images = [imageio.imread(img_path) for img_path in img_paths]
imageio.mimsave(gif_path, images, duration=0.5)  # duration controls the speed of the gif
