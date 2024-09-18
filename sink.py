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

GREEN_ABSORPTION_RATE = 22
WETLANDS_ABSORPTION_RATE = 5.0

TREE_CO2_MIN = 10
TREE_CO2_MAX = 40

PIXEL_TO_METER_CONVERSION = 0.5

def find_chrome_path_windows():
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            return winreg.QueryValueEx(key, None)[0]
    except FileNotFoundError:
        return None

def get_chrome_path():
    if sys.platform.startswith('win'):
        return find_chrome_path_windows()
    else:
        return None

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
    chrome_path = get_chrome_path()
    
    if not chrome_path:
        print("Google Chrome is not installed or not found.")
        return
    
    print(f"Using Chrome path: {chrome_path}")

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
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        latitude = float(input("Enter the latitude: "))
        longitude = float(input("Enter the longitude: "))
        
        driver.get(f"https://www.google.com/maps/@{latitude},{longitude},10z/data=!5m1!1e4")

        # Wait until the map loads completely
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="searchboxinput"]'))
        )

        screenshot = driver.get_screenshot_as_png()

        img = Image.open(io.BytesIO(screenshot))
        img_path = "screenshot.png"
        img.save(img_path)

        results = analyze_image(img_path)
        
        actual_emissions = float(input("Enter the actual CO₂ emissions (kg): "))
        
        print(f"Total CO₂ Absorption: {results['total_absorption']:.2f} kg")
        print(f"Trees Needed: {results['trees_needed_min']:.2f} - {results['trees_needed_max']:.2f}")

        sink_gap = actual_emissions - results['total_absorption']
        
        print(f"CO₂ Sink Gap Analysis:")
        print(f"Total CO₂ Emissions: {actual_emissions:.2f} kg")
        print(f"Total CO₂ Absorption: {results['total_absorption']:.2f} kg")
        print(f"CO₂ Sink Gap: {sink_gap:.2f} kg")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
