import sys
import subprocess
import winreg
import cv2
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import io
import pandas as pd

# Constants for absorption rates and tree CO2 absorption
GREEN_ABSORPTION_RATE = 22  # kg CO2 per m² per year for green areas
WETLANDS_ABSORPTION_RATE = 5.0  # kg CO2 per m² per year for wetlands

TREE_CO2_MIN = 10  # kg CO2 per tree per year (low estimate)
TREE_CO2_MAX = 40  # kg CO2 per tree per year (high estimate)

PIXEL_TO_METER_CONVERSION = 0.5  # 1 pixel = 0.5 meters (placeholder)

# Load afforestation policies data from CSV
def load_afforestation_policies(csv_file_path):
    return pd.read_csv(csv_file_path)

# Function to find the path to Chrome on Windows
def find_chrome_path_windows():
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            return winreg.QueryValueEx(key, None)[0]
    except FileNotFoundError:
        return None

# Function to get the Chrome browser path based on the operating system
def get_chrome_path():
    if sys.platform.startswith('win'):
        return find_chrome_path_windows()
    else:
        return None

# Function to analyze the image for green and blue areas
def analyze_image(image_path):
    img = cv2.imread(image_path)
    
    if img is None:
        return {
            "green_pct": 0.0, "blue_pct": 0.0, 
            "green_absorption": 0.0, "wetlands_absorption": 0.0, 
            "total_absorption": 0.0, "trees_needed_min": 0, 
            "trees_needed_max": 0
        }
    
    # Convert image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_np = np.array(img_rgb)
    
    # Define color ranges for green and blue areas (in RGB)
    lower_green = np.array([0, 100, 0])
    upper_green = np.array([100, 255, 100])
    
    lower_blue = np.array([0, 0, 100])
    upper_blue = np.array([100, 100, 255])
    
    # Masking green and blue areas
    mask_green = cv2.inRange(img_np, lower_green, upper_green)
    mask_blue = cv2.inRange(img_np, lower_blue, upper_blue)
    
    total_pixels = img_np.size / 3
    
    green_pixels = cv2.countNonZero(mask_green)
    blue_pixels = cv2.countNonZero(mask_blue)
    
    green_pct = (green_pixels / total_pixels) * 100
    blue_pct = (blue_pixels / total_pixels) * 100
    
    # Real-world area conversion based on image dimensions and pixel-to-meter ratio
    img_height, img_width, _ = img_np.shape
    real_world_area_m2 = img_height * img_width * PIXEL_TO_METER_CONVERSION**2
    
    # Calculate green and blue areas in square meters
    green_area_m2 = (green_pixels / total_pixels) * real_world_area_m2
    blue_area_m2 = (blue_pixels / total_pixels) * real_world_area_m2
    
    # Calculate absorption potential
    green_absorption = green_area_m2 * GREEN_ABSORPTION_RATE
    wetlands_absorption = blue_area_m2 * WETLANDS_ABSORPTION_RATE
    
    # Total absorption is the sum of green and wetlands absorption
    total_absorption = green_absorption + wetlands_absorption
    
    # Calculate the number of trees needed to offset emissions
    trees_needed_min = total_absorption / TREE_CO2_MAX
    trees_needed_max = total_absorption / TREE_CO2_MIN
    
    return {
        "green_pct": green_pct,
        "blue_pct": blue_pct,
        "green_absorption": green_absorption,
        "wetlands_absorption": wetlands_absorption,
        "total_absorption": total_absorption,
        "trees_needed_min": trees_needed_min,
        "trees_needed_max": trees_needed_max
    }

# Function to apply state-specific afforestation policy data
def apply_afforestation_policy(state, emission_gap, policy_data):
    state_policy = policy_data[policy_data['State'].str.lower() == state.lower()]
    
    if not state_policy.empty:
        # Example: Get planting species and adjust absorption rates
        species = state_policy['Planting Species'].values[0]
        target_area = state_policy['Target Area (in hectares)'].values[0]
        
        # Placeholder: You can adjust the absorption rate based on the species if you have detailed data
        adjusted_absorption_rate = GREEN_ABSORPTION_RATE  # This can be customized based on the species
        
        # Use the policy's target area to calculate potential absorption
        afforestation_potential = target_area * 10000 * adjusted_absorption_rate  # hectares to m²
        
        if afforestation_potential >= emission_gap:
            return f"State policy '{state_policy['Policy Name'].values[0]}' can absorb {afforestation_potential:.2f} kg of CO₂, which is sufficient to offset the remaining emissions."
        else:
            return f"State policy '{state_policy['Policy Name'].values[0]}' can absorb {afforestation_potential:.2f} kg of CO₂, but additional afforestation is needed to cover the remaining gap of {emission_gap - afforestation_potential:.2f} kg."
    
    return "No specific policy found for this state."

# Main function to run the image analysis and emission calculation
def main():
    # Get the path to Chrome
    chrome_path = get_chrome_path()
    
    if not chrome_path:
        print("Google Chrome is not installed or not found.")
        return
    
    print(f"Using Chrome path: {chrome_path}")

    # Set Chrome options for headless browsing and other optimizations
    chrome_options = Options()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--window-size=1920x1080")  # Set window size for screenshots
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    
    try:
        # Load afforestation policy data
        afforestation_data = load_afforestation_policies('afforestation_policies_indian_states.csv')
        
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Ask for the latitude and longitude inputs
        latitude = float(input("Enter the latitude: "))
        longitude = float(input("Enter the longitude: "))
        state = input("Enter the state: ")
        
        # Load the location in Google Maps
        driver.get(f"https://www.google.com/maps/@{latitude},{longitude},10z/data=!5m1!1e4")

        # Wait for the map to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="searchboxinput"]'))
        )

        # Take a screenshot of the map
        screenshot = driver.get_screenshot_as_png()

        # Save the screenshot as an image file
        img = Image.open(io.BytesIO(screenshot))
        img_path = "screenshot.png"
        img.save(img_path)

        # Analyze the screenshot for green and blue areas
        results = analyze_image(img_path)
        
        # Input the actual CO₂ emissions
        actual_emissions = float(input("Enter the actual CO₂ emissions (kg): "))
        
        # Display results for total absorption and tree requirements
        print(f"Total CO₂ Absorption: {results['total_absorption']:.2f} kg")
        print(f"Trees Needed: {results['trees_needed_min']:.2f} - {results['trees_needed_max']:.2f}")

        # Calculate the CO₂ sink gap (difference between emissions and absorption)
        sink_gap = actual_emissions - results['total_absorption']
        
        # Print CO₂ sink gap analysis
        print(f"CO₂ Sink Gap Analysis:")
        print(f"Total CO₂ Emissions: {actual_emissions:.2f} kg")
        print(f"Total CO₂ Absorption: {results['total_absorption']:.2f} kg")
        print(f"CO₂ Sink Gap: {sink_gap:.2f} kg")
        
        # Apply state-specific afforestation policy
        policy_recommendation = apply_afforestation_policy(state, sink_gap, afforestation_data)
        print(policy_recommendation)
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Quit the Chrome driver if it was initialized
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
