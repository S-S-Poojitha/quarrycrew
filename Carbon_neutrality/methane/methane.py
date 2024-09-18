import numpy as np

# Constants
METHANE_MW = 16.04  # Molecular weight of methane in g/mol
GAS_CONSTANT = 22.41  # Volume of 1 mole of gas at STP in liters
METHANE_ENERGY_CONTENT_MJ_PER_KG = 55.5  # Energy content of methane in MJ/kg

# Default values
EMISSION_FACTOR_KG_PER_TON = 10  # Methane emission factor for coal mining (kg CH4/ton of coal)
AIR_FLOW_M3_PER_S = 100  # Air flow rate in m³/s
METHANE_CONCENTRATION_PPM = 5000  # Methane concentration in ppm
OPERATION_TIME_HOURS = 10  # Mining operation time in hours
OVERBURDEN_VOLUME_M3 = 10000  # Overburden volume in cubic meters
METHANE_CONCENTRATION_M3_PER_M3 = 0.01  # Methane concentration in overburden (m³ CH4 per m³ overburden)
CAPTURE_EFFICIENCY = 0.8  # Methane capture efficiency (80%)

# Function to calculate methane emissions based on coal mined and emission factors
def calculate_methane_emissions_from_coal(coal_mined_tons, emission_factor_kg_per_ton):
    return coal_mined_tons * emission_factor_kg_per_ton

# Function to calculate methane emissions from direct measurement
def calculate_methane_emissions_direct(air_flow_m3_per_s, methane_concentration_ppm, operation_time_hours):
    methane_fraction = methane_concentration_ppm / 1_000_000
    total_air_volume_m3 = air_flow_m3_per_s * (operation_time_hours * 3600)
    methane_volume_m3 = total_air_volume_m3 * methane_fraction
    methane_mass_kg = (methane_volume_m3 * METHANE_MW) / GAS_CONSTANT
    return methane_mass_kg

# Function to calculate methane emissions from overburden
def calculate_methane_emissions_from_overburden(overburden_volume_m3, methane_concentration_m3_per_m3):
    return overburden_volume_m3 * methane_concentration_m3_per_m3

# Function to calculate methane captured based on capture efficiency
def calculate_methane_captured(methane_emissions_kg, capture_efficiency):
    return methane_emissions_kg * capture_efficiency

# Function to calculate energy generated from captured methane
def calculate_energy_from_methane(methane_captured_kg):
    return methane_captured_kg * METHANE_ENERGY_CONTENT_MJ_PER_KG

# User Input: Enter the amount of coal mined (tons)
coal_mined_tons = float(input("Enter the amount of coal mined (tons): "))

# Calculations using default values for other parameters
methane_emissions_coal = calculate_methane_emissions_from_coal(coal_mined_tons, EMISSION_FACTOR_KG_PER_TON)
print(f"Methane Emissions from Coal Mined: {methane_emissions_coal:.2f} kg")

methane_emissions_direct = calculate_methane_emissions_direct(AIR_FLOW_M3_PER_S, METHANE_CONCENTRATION_PPM, OPERATION_TIME_HOURS)
print(f"Methane Emissions from Direct Measurement: {methane_emissions_direct:.2f} kg")

methane_emissions_overburden = calculate_methane_emissions_from_overburden(OVERBURDEN_VOLUME_M3, METHANE_CONCENTRATION_M3_PER_M3)
print(f"Methane Emissions from Overburden: {methane_emissions_overburden:.2f} m³")

methane_emissions_overburden_kg = (methane_emissions_overburden * METHANE_MW) / GAS_CONSTANT

# Methane capture and energy generation
methane_captured_coal = calculate_methane_captured(methane_emissions_coal, CAPTURE_EFFICIENCY)
energy_generated_coal = calculate_energy_from_methane(methane_captured_coal)
print(f"Methane Captured from Coal Mined: {methane_captured_coal:.2f} kg")
print(f"Energy Generated from Captured Methane (Coal): {energy_generated_coal:.2f} MJ")

methane_captured_direct = calculate_methane_captured(methane_emissions_direct, CAPTURE_EFFICIENCY)
energy_generated_direct = calculate_energy_from_methane(methane_captured_direct)
print(f"Methane Captured from Direct Measurement: {methane_captured_direct:.2f} kg")
print(f"Energy Generated from Captured Methane (Direct): {energy_generated_direct:.2f} MJ")

methane_captured_overburden = calculate_methane_captured(methane_emissions_overburden_kg, CAPTURE_EFFICIENCY)
energy_generated_overburden = calculate_energy_from_methane(methane_captured_overburden)
print(f"Methane Captured from Overburden: {methane_captured_overburden:.2f} kg")
print(f"Energy Generated from Captured Methane (Overburden): {energy_generated_overburden:.2f} MJ")
