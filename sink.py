import sys
import cv2
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import io

GREEN_ABSORPTION_RATE = 22
WETLANDS_ABSORPTION_RATE = 5.0

TREE_CO2_MIN = 10
TREE_CO2_MAX = 40

PIXEL_TO_METER_CONVERSION = 0.5

def analyze_image(image_path):
    img = cv2.imread(image_path)
    
    if img is None:
        return {
            "green_pct": 0.0, "blue_pct": 0.0, 
            "green_absorption": 0.0, "wetlands_absorption": 0.0, 
            "total_absorption": 0.0, "trees_needed_min": 0, 
            "trees_needed_max": 0
        }
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_np = np.array(img_rgb)
    
    lower_green = np.array([0, 100, 0])
    upper_green = np.array([100, 255, 100])
    
    lower_blue = np.array([0, 0, 100])
    upper_blue = np.array([100, 100, 255])
    
    lower_white = np.array([200, 200, 200])
    upper_white = np.array([255, 255, 255])
    
    mask_green = cv2.inRange(img_np, lower_green, upper_green)
    mask_blue = cv2.inRange(img_np, lower_blue, upper_blue)
    
    mask_white = cv2.inRange(img_np, lower_white, upper_white)
    mask_non_white = cv2.bitwise_not(mask_white)
    mask_green = cv2.bitwise_and(mask_green, mask_non_white)
    mask_blue = cv2.bitwise_and(mask_blue, mask_non_white)
    
    total_pixels = img_np.size / 3
    
    green_pixels = cv2.countNonZero(mask_green)
    blue_pixels = cv2.countNonZero(mask_blue)
    
    green_pct = (green_pixels / total_pixels) * 100
    blue_pct = (blue_pixels / total_pixels) * 100
    
    img_height, img_width, _ = img_np.shape
    real_world_area_m2 = img_height * img_width * PIXEL_TO_METER_CONVERSION**2
    
    green_area_m2 = (green_pixels / total_pixels) * real_world_area_m2
    blue_area_m2 = (blue_pixels / total_pixels) * real_world_area_m2
    
    green_absorption = green_area_m2 * GREEN_ABSORPTION_RATE
    wetlands_absorption = blue_area_m2 * WETLANDS_ABSORPTION_RATE
    
    total_absorption = green_absorption + wetlands_absorption
    
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

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Ask for the latitude and longitude inputs
        latitude = float(input("Enter the latitude: "))
        longitude = float(input("Enter the longitude: "))
        
        # Load the location in Google Maps
        page.goto(f"https://www.google.com/maps/@{latitude},{longitude},10z/data=!5m1!1e4")
        
        # Wait for the map to load
        page.wait_for_selector('//*[@id="searchboxinput"]', timeout=20000)
        
        # Take a screenshot of the map
        screenshot = page.screenshot(full_page=True)
        
        # Save the screenshot as an image file
        img_path = "screenshot.png"
        with open(img_path, "wb") as f:
            f.write(screenshot)
        
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
    
        # Close the browser
        browser.close()

if __name__ == "__main__":
    main()
