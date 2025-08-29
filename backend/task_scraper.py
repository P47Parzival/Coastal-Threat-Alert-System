# In a new file, e.g., backend/tasks_scraper.py
from celery_config import celery_app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Helper function to convert GeoJSON to Bounding Box
def get_bbox_from_geojson(geojson):
    # This logic extracts the min/max lat/lon from the GeoJSON coordinates
    coords = geojson['coordinates'][0]
    min_lon = min(p[0] for p in coords)
    max_lon = max(p[0] for p in coords)
    min_lat = min(p[1] for p in coords)
    max_lat = max(p[1] for p in coords)
    return min_lon, min_lat, max_lon, max_lat

@celery_app.task
def download_liss4_data_for_aoi(aoi_id: str):
    # Setup Chrome options for headless mode and automatic downloads
    chrome_options = webdriver.ChromeOptions()
    # IMPORTANT: Define a specific download directory for this task's data
    download_path = f"/var/data/downloads/{aoi_id}" 
    prefs = {"download.default_directory": download_path}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless") # Run without opening a GUI window
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Step 1: Get AOI data
        # aoi_doc = fetch_from_db(aoi_id)
        # min_lon, min_lat, max_lon, max_lat = get_bbox_from_geojson(aoi_doc['AOI_geojson'])

        # Step 2: Login
        driver.get("https://bhoonidhi.nrsc.gov.in/bhoonidhi/index.html")
        # Use WebDriverWait to ensure elements are present before interacting
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("your_bhoonidhi_user")
        driver.find_element(By.ID, "password").send_keys("your_bhoonidhi_pass")
        driver.find_element(By.ID, "loginbtn").click()
        
        print(f"Logged into Bhoonidhi for AOI {aoi_id}")
        time.sleep(5) # Wait for login redirect to complete

        # Step 3: Search for data using the AOI's bounding box and dates
        # This part is highly specific to Bhoonidhi's UI. You must inspect 
        # the HTML to find the correct IDs/XPaths for:
        # - The satellite dropdown ('Resourcesat-2')
        # - The sensor dropdown ('LISS-4')
        # - The bounding box input fields
        # - The date range pickers
        # - The search button
        
        print("Searching for LISS-4 scenes...")
        # ... your code to fill the form and click search ...
        time.sleep(10) # Wait for search results to load

        # Step 4: Find and click download links
        # This also requires inspecting the results table HTML
        # download_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'download-link-class')]")
        # for link in download_links:
        #     link.click()
        #     time.sleep(2) # Give a moment between clicks
        
        print(f"Downloads initiated. Files are being saved to {download_path}")
        # You might need to monitor the download directory to know when files are complete.

        # Step 5: Trigger ML pipeline
        # run_custom_ml_pipeline.delay(aoi_id, download_path)

    except Exception as e:
        print(f"An error occurred during scraping for AOI {aoi_id}: {e}")
    finally:
        driver.quit()

    return f"Scraping process completed for {aoi_id}."