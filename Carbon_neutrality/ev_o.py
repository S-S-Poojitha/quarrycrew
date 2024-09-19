import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Example dataset
data = {
    'vehicle_type': [0, 0, 0, 1, 1, 1],  # 0 = traditional, 1 = EV
    'distance_traveled_km': [100, 150, 200, 100, 150, 200],
    'fuel_consumption_liters': [10, 15, 20, 0, 0, 0],  # 0 for EV
    'energy_consumption_kwh': [0, 0, 0, 20, 30, 40],  # Only for EVs
    'grid_emission_factor': [0, 0, 0, 0.2, 0.2, 0.2],  # g CO2/kWh for EVs
    'traditional_emission_factor': [250, 250, 250, 0, 0, 0],  # g CO2/km for traditional vehicles
    'emissions': [2500, 3750, 5000, 400, 600, 800]  # Pre-calculated emissions in grams
}

# Create a DataFrame
df = pd.DataFrame(data)

# Define features and target
X = df[['vehicle_type', 'distance_traveled_km', 'fuel_consumption_liters', 'energy_consumption_kwh', 'grid_emission_factor', 'traditional_emission_factor']]
y = df['emissions']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create an XGBoost regressor model
model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1)

# Train the model
model.fit(X_train, y_train)

# Predict emissions for the test set
y_pred = model.predict(X_test)

# Evaluate model performance
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"Root Mean Squared Error: {rmse:.2f}")

# Example new data for emission prediction (before and after switching to EV)
new_data = pd.DataFrame({
    'vehicle_type': [0, 1],  # 0 = traditional, 1 = EV
    'distance_traveled_km': [120, 120],  # Same distance
    'fuel_consumption_liters': [12, 0],  # Traditional uses fuel, EV uses none
    'energy_consumption_kwh': [0, 24],  # EV uses energy in kWh
    'grid_emission_factor': [0, 0.2],  # Grid emission factor for EV
    'traditional_emission_factor': [250, 0]  # Emission factor for traditional
})

# Predict emissions for the new data
predictions = model.predict(new_data)
print(f"Predicted emissions (Traditional): {predictions[0]:.2f} grams CO2")
print(f"Predicted emissions (EV): {predictions[1]:.2f} grams CO2")

# Recommendation: If emissions reduction is significant, recommend EV adoption
if predictions[1] < predictions[0]:
    print("Recommendation: Switch to EV for emissions reduction.")
else:
    print("Recommendation: Traditional vehicles may be more suitable based on current grid conditions.")
