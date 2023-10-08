import numpy as np
import math
import pandas as pd

# Parameters
max_capacity = 200  # Maximum capacity of a vehicle
min_departures, max_departures = 1, 10  # Minimum and maximum number of departures per hour
initial_temp, final_temp = 1000, 1  # Initial and final temperature for simulated annealing
alpha = 0.9  # Cooling rate
max_iter = 1000  # Maximum iterations at a given temperature

# Adjusted weights
w1, w2_day, w2_night, w3 = 0.0002, 0.1, 0.15, 6

import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Convert transit_timestamp to datetime object and extract hour and weekday
mta_data=pd.read_csv('MTA_Subway_Hourly_Ridership__Beginning_February_2022.csv').iloc[:1000]
# mta_data=pd.read_csv('MTA_100000.csv')
mta_data['transit_timestamp'] = pd.to_datetime(mta_data['transit_timestamp'], format='%m/%d/%Y %I:%M:%S %p')
mta_data['hour'] = mta_data['transit_timestamp'].dt.hour
mta_data['weekday'] = mta_data['transit_timestamp'].dt.weekday

# Aggregate data to get average ridership for each hour of each day of the week
avg_ridership = mta_data.groupby(['weekday', 'hour'])['ridership'].mean().reset_index()


def cost_function(schedule, avg_ridership_by_hour, w1, w2_day, w2_night, w3, max_capacity):
    """
    Cost function to evaluate a schedule based on
    - total waiting time for passengers,
    - total number of departures, and
    - total crowdiness.

    The weights w1, w2, and w3 are used to balance the three components based on their magnitude.
    """
    total_waiting_time = sum(
        [60 / departures for departures in schedule])  # Assuming waiting time is 60 min / number of departures
    total_crowdiness = sum([min(ridership, max_capacity) for ridership in
                            avg_ridership_by_hour])  # Number of people in the vehicle, capped at max_capacity

    # Different costs for day and night
    total_departures_day = sum([schedule[i] for i in range(9, 18)])  # from 9 AM to 5 PM
    total_departures_night = sum(schedule) - total_departures_day  # the rest of the day/night

    cost = (w1 * total_waiting_time +
            w2_day * total_departures_day +
            w2_night * total_departures_night +
            w3 * total_crowdiness)

    return cost

# Initialize dictionaries to store the optimal schedules and costs for each day of the week
optimal_schedules = {}
optimal_costs = {}


def simulated_annealing(initial_schedule, avg_ridership_by_hour, w1, w2_day, w2_night, w3, max_capacity,
                        initial_temp, final_temp, alpha, max_iter):
    """
    Simulated Annealing Algorithm to find the optimal schedule considering
    - total waiting time for passengers,
    - total number of departures, and
    - total crowdiness.
    """
    current_schedule = initial_schedule.copy()
    current_cost = cost_function(current_schedule, avg_ridership_by_hour, w1, w2_day, w2_night, w3, max_capacity)

    current_temp = initial_temp

    while current_temp > final_temp:
        for _ in range(max_iter):
            # Generate a neighbor solution
            new_schedule = current_schedule.copy()
            hour_to_change = np.random.randint(0, 24)  # Randomly select an hour to change
            new_schedule[hour_to_change] = np.random.randint(min_departures,
                                                             max_departures + 1)  # Randomly assign a new number of departures

            # Calculate the new cost
            new_cost = cost_function(new_schedule, avg_ridership_by_hour, w1, w2_day, w2_night, w3, max_capacity)

            # Determine if we should accept the new solution
            cost_diff = new_cost - current_cost
            if cost_diff < 0 or np.random.rand() < math.exp(-cost_diff / current_temp):
                current_schedule, current_cost = new_schedule, new_cost

        # Cool down
        current_temp *= alpha

    return current_schedule, current_cost


# Run simulated annealing for each day of the week
for weekday in range(7):
    # Extract average ridership by hour for the specific day
    avg_ridership_day = avg_ridership[avg_ridership['weekday'] == weekday].groupby('hour')['ridership'].mean().values

    # Initial schedule (randomly assigned within allowed range)
    initial_schedule_day = np.random.randint(min_departures, max_departures + 1, size=24)

    # Run simulated annealing
    optimal_schedule_day, optimal_cost_day = simulated_annealing(
        initial_schedule_day, avg_ridership_day, w1, w2_day, w2_night, w3, max_capacity, initial_temp, final_temp,
        alpha, max_iter
    )

    # Store the results
    optimal_schedules[weekday] = optimal_schedule_day
    optimal_costs[weekday] = optimal_cost_day

# Display optimal schedules and costs for each day
print(optimal_schedules)
print(optimal_costs)
