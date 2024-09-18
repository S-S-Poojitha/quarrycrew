import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller

# Load data from CSV, skipping the first 19 rows
df = pd.read_csv('geothermal_data.csv', skiprows=18)

# Filter for the TS parameter and set the index
df = df[df['PARAMETER'] == 'TS']
df.set_index('YEAR', inplace=True)

# Ensure the index is a datetime type
df.index = pd.to_datetime(df.index.astype(str))

# Check for stationarity
result = adfuller(df['ANN'])
print('ADF Statistic:', result[0])
print('p-value:', result[1])

# Fit SARIMA model
model = SARIMAX(df['ANN'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
results = model.fit()

# Print model summary
print(results.summary())

# Forecast future values
n_years = 5  # Number of years to predict
future_dates = pd.date_range(start=df.index[-1] + pd.DateOffset(years=1), periods=n_years, freq='Y')
forecast = results.get_forecast(steps=n_years)
forecast_values = forecast.predicted_mean

# Constants for geothermal energy calculation
flow_rate = 100  # Flow rate in L/s
reservoir_depth = 2  # Depth in km
temperature_gradient = 25  # °C/km
efficiency = 0.15  # 15% efficiency

# Calculate the expected reservoir temperature based on the last observed temperature
initial_temp = df['ANN'].iloc[-1]
reservoir_temp = initial_temp + (reservoir_depth * temperature_gradient)

# Calculate temperature increase
temperature_increase = reservoir_temp - initial_temp

# Calculate energy produced for each forecasted year
energy_produced = []
for temp in forecast_values:
    energy = flow_rate * (temp - initial_temp) * 4.18 * 3600 * efficiency  # in kWh
    energy_produced.append(energy)

# Prepare DataFrame for forecasted values and energy production
forecast_df = pd.DataFrame({
    'Forecast': forecast_values,
    'Energy Produced (kWh)': energy_produced
}, index=future_dates)

# Display forecasted temperature and energy produced
print(forecast_df)

# Plot Energy Production as a Curve
plt.figure(figsize=(10, 6))
plt.plot(forecast_df.index, forecast_df['Energy Produced (kWh)'], marker='o', linestyle='-', color='orange', alpha=0.7)
plt.title('Estimated Geothermal Energy Production')
plt.xlabel('Year')
plt.ylabel('Energy Produced (kWh)')
plt.grid()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()