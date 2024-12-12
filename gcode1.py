from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Google Maps URL
url = "https://www.google.com/maps/place/NAMI+Southeastern+Arizona/@31.5358518,-110.2590357,17z/data=!3m1!4b1!4m6!3m5!1s0x86d7291bd0224037:0xa4f8e71bef622256!8m2!3d31.5358473!4d-110.2564608!16s%2Fg%2F1hc528cnt?entry=ttu&g_ep=EgoyMDI0MTEyNC4xIKXMDSoASAFQAw%3D%3D"

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Enable headless mode
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer
options.add_argument("--log-level=3")  # Suppress logs
options.add_argument("--enable-unsafe-swiftshader")  # Enable SwiftShader (if needed)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Open the Google Maps link
    driver.get(url)
    
    # Wait for the address element to load
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
    address_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Io6YTe")))

    # Get the address text
    address = address_element.text
    print("Address:", address)

except Exception as e:
    print("An error occurred:", e)
finally:
    # Quit the driver
    driver.quit()
