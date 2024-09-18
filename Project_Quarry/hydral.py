import pandas as pd
import numpy as np
from haversine import haversine, Unit

# Step 1: Load the data
data = pd.read_csv('hydropower_data.csv')  # Replace with your actual file path
print(data.head())

# Step 2: Handle missing values
data['Lat (reservoir/dam)'].fillna(np.nan, inplace=True)
data['Long (reservoir/dam)'].fillna(np.nan, inplace=True)
data['Lat (hydropower station 1)'].fillna(np.nan, inplace=True)
data['Long (hydropower station 1)'].fillna(np.nan, inplace=True)
data['Lat (hydropower station 2)'].fillna(np.nan, inplace=True)
data['Long (hydropower station 2)'].fillna(np.nan, inplace=True)
data['WaterHeadhgt( max)'].fillna(data['WaterHeadhgt( max)'].mean(), inplace=True)
data['Res_capacityMm3'].fillna(0, inplace=True)
data.dropna(subset=['Lat (reservoir/dam)', 'Long (reservoir/dam)'], inplace=True)

# Step 3: Get user input for the location
input_lat = float(input("Enter your latitude: "))
input_long = float(input("Enter your longitude: "))
input_location = (input_lat, input_long)

# Step 4: Calculate proximity (distance) between user location and hydropower stations
def calculate_distance(row):
    distances = {}
    
    if pd.notnull(row['Lat (reservoir/dam)']) and pd.notnull(row['Long (reservoir/dam)']):
        reservoir_point = (row['Lat (reservoir/dam)'], row['Long (reservoir/dam)'])
        
        # Calculate distance to Hydropower Station 1
        if pd.notnull(row['Lat (hydropower station 1)']) and pd.notnull(row['Long (hydropower station 1)']):
            hydro1_point = (row['Lat (hydropower station 1)'], row['Long (hydropower station 1)'])
            dist_to_hydro1 = haversine(input_location, hydro1_point, unit=Unit.KILOMETERS)
        else:
            dist_to_hydro1 = np.nan

        # Calculate distance to Hydropower Station 2
        if pd.notnull(row['Lat (hydropower station 2)']) and pd.notnull(row['Long (hydropower station 2)']):
            hydro2_point = (row['Lat (hydropower station 2)'], row['Long (hydropower station 2)'])
            dist_to_hydro2 = haversine(input_location, hydro2_point, unit=Unit.KILOMETERS)
        else:
            dist_to_hydro2 = np.nan

        distances['Distance_to_Hydro1_km'] = dist_to_hydro1
        distances['Distance_to_Hydro2_km'] = dist_to_hydro2
    else:
        distances['Distance_to_Hydro1_km'] = np.nan
        distances['Distance_to_Hydro2_km'] = np.nan
    
    return pd.Series(distances)

# Apply the function to calculate distances
data[['Distance_to_Hydro1_km', 'Distance_to_Hydro2_km']] = data.apply(calculate_distance, axis=1)

# Step 5: Filter for nearby stations (e.g., within 500 km)
distance_threshold_km = 500
nearby_stations = data[(data['Distance_to_Hydro1_km'] <= distance_threshold_km) | 
                       (data['Distance_to_Hydro2_km'] <= distance_threshold_km)]

# Step 6: Calculate potential hydropower for nearby stations
def calculate_hydropower_potential(row):
    gravity = 9.81
    efficiency = 0.9
    conversion_factor = 1e6  # Convert to MW

    water_head = row['WaterHeadhgt( max)']
    reservoir_capacity = row['Res_capacityMm3'] * 1e6  # Convert Mm³ to m³

    if pd.notnull(water_head) and pd.notnull(reservoir_capacity):
        total_potential_power = (reservoir_capacity * water_head * efficiency * gravity) / conversion_factor
        # Calculate 40% of the total potential power
        potential_power = total_potential_power * 0.4
    else:
        potential_power = np.nan
    
    return potential_power

# Apply the potential calculation function to nearby stations
nearby_stations['Hydropower_Potential_MW'] = nearby_stations.apply(calculate_hydropower_potential, axis=1)

# Step 7: Display or save the results for nearby stations
print("\nHydropower stations near your location:")
print(nearby_stations[['Hydropower Station Name', 'Distance_to_Hydro1_km', 'Distance_to_Hydro2_km', 'Hydropower_Potential_MW']])

# Save results to CSV file
nearby_stations.to_csv('nearby_hydro_stations.csv', index=False)
