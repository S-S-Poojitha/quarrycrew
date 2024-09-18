import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures
from statsmodels.tsa.arima.model import ARIMA

# Load the dataset
file_path = "renewable.csv"
df = pd.read_csv(file_path, skiprows=24)

# Set the parameter as the index
df.set_index('PARAMETER', inplace=True)

# Function to calculate the annual average for each parameter
def calculate_annual_average(df):
    annual_averages = df.loc[:, 'JAN':'DEC'].mean(axis=1)
    df['ANN'] = annual_averages
    return df

# Calculate the annual average values
df = calculate_annual_average(df)

# Extract relevant parameters for analysis
temperature = df.loc['T2M']
humidity = df.loc['RH2M']
wind_speed_50m = df.loc['WS50M']
solar_irradiance = df.loc['ALLSKY_SFC_SW_DWN']

# Prepare features
features = np.column_stack((temperature['ANN'], humidity['ANN'], wind_speed_50m['ANN'], solar_irradiance['ANN']))

# Placeholder energy production values (Replace these with actual data if available)
energy_production = np.random.uniform(low=500, high=2000, size=len(features))

# Emission factors (in kg CO2 per kWh)
emission_factor_non_renewable = 0.9
emission_factor_renewable = 0.1

# Calculate current emissions
current_emissions_non_renewable = energy_production * emission_factor_non_renewable
current_emissions_renewable = energy_production * emission_factor_renewable

# Polynomial features for Gradient Boosting
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(features)

# Gradient Boosting model
gb_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
gb_model.fit(X_poly, current_emissions_non_renewable)

# Define a time range for predictions
years = np.arange(2024, 2024 + 10)  # Predicting for the next 10 years

# Create a grid of future feature values with controlled ranges
future_temps = np.linspace(temperature['ANN'].min(), temperature['ANN'].max(), len(years))
future_humidities = np.linspace(humidity['ANN'].min(), humidity['ANN'].max(), len(years))
future_wind_speeds = np.linspace(wind_speed_50m['ANN'].min(), wind_speed_50m['ANN'].max(), len(years))
future_solar_irradiances = np.linspace(solar_irradiance['ANN'].min(), solar_irradiance['ANN'].max(), len(years))

# Create a grid of future feature values
future_features = np.column_stack((future_temps, future_humidities, future_wind_speeds, future_solar_irradiances))
future_X_poly = poly.transform(future_features)

# Predict future emissions using Gradient Boosting for non-renewable energy
future_emissions_non_renewable = gb_model.predict(future_X_poly)
# Calculate future renewable emissions based on non-renewable predictions
future_emissions_renewable = future_emissions_non_renewable / emission_factor_non_renewable * emission_factor_renewable

# ARIMA model for energy production forecasting
# Define an ARIMA model (p, d, q) for the energy production time series
model = ARIMA(energy_production, order=(5, 1, 0))  # Adjust (p, d, q) for your data
model_fit = model.fit()

# Forecast future energy production for the next 10 years
energy_production_forecast = model_fit.forecast(steps=len(years))

# Plotting results
plt.figure(figsize=(12, 6))

# Plot future emissions for non-renewable energy
plt.plot(years, future_emissions_non_renewable, color='red', linestyle='--', marker='o', label='Future Emissions (Non-Renewable)')

# Plot future emissions for renewable energy
plt.plot(years, future_emissions_renewable, color='green', linestyle='--', marker='x', label='Future Emissions (Renewable)')

# Plot future energy production (ARIMA forecast)
plt.plot(years, energy_production_forecast, color='blue', linestyle='-', marker='s', label='Energy Production (ARIMA Forecast)')

plt.xlabel('Year')
plt.ylabel('Emissions (kg CO2) / Energy Production')
plt.title('Future Emissions and Energy Production Forecast Over the Next 10 Years')
plt.legend()
plt.grid(True)
plt.show()
