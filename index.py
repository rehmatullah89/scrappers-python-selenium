import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class GeneralizedScraper:
    def __init__(self, input_csv, output_csv):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.driver = None
        self.initialize_driver()

        # Initialize the CSV with headers
        self.initialize_csv()

    def initialize_driver(self):
        """Initialize the Selenium ChromeDriver."""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")  # Open browser in maximized mode
        options.add_argument("--disable-gpu")  # Disable GPU acceleration
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--log-level=3")  # Suppress logs
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def initialize_csv(self):
        """Initialize the output CSV file with headers."""
        fieldnames = ["Domain", "Company", "Address", "City", "State", "Zip"]
        with open(self.output_csv, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()

    def get_domains_from_csv(self):
        """Read domains from the input CSV file."""
        with open(self.input_csv, "r") as file:
            reader = csv.reader(file)
            return [row[0] for row in reader if row]  # Ensure non-empty rows

    def scrape_google_maps(self, domain):
        """Scrape Google Maps for the title (company name) and address."""
        try:
            # Open Google Maps and search for the domain
            self.driver.get("https://www.google.com/maps")
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(domain)
            self.driver.find_element(By.ID, "searchbox-searchbutton").click()

            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Io6YTe"))
            )

            # Extract the title (company name) and address
            company_name = self._get_text(By.XPATH, '//h1[contains(@class,"DUwDvf")]')
            full_address = self._get_text(By.CLASS_NAME, "Io6YTe")

            # Split the address into components
            address, city, state, zip_code = self.split_address(full_address)

            result = {
                "Domain": domain,
                "Company": company_name if company_name else "Not Found",
                "Address": address if address else "Not Found",
                "City": city if city else "Not Found",
                "State": state if state else "Not Found",
                "Zip": zip_code if zip_code else "Not Found",
            }
            print(f"Scraped Data for {domain}: {result}")

            # Write this result to the CSV file immediately
            self.write_to_csv(result)

        except TimeoutException:
            print(f"Timeout: No results found for {domain}")
            self.write_to_csv(
                {"Domain": domain, "Company": "Not Found", "Address": "Not Found", "City": "Not Found", "State": "Not Found", "Zip": "Not Found"}
            )
        except Exception as e:
            print(f"Error scraping {domain}: {e}")
            self.write_to_csv(
                {"Domain": domain, "Company": "Error", "Address": "Error", "City": "Error", "State": "Error", "Zip": "Error"}
            )

    def write_to_csv(self, data):
        """Write a single result to the output CSV file."""
        fieldnames = ["Domain", "Company", "Address", "City", "State", "Zip"]
        with open(self.output_csv, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writerow(data)

    def _get_text(self, by, value):
        """Get text from a web element."""
        try:
            return self.driver.find_element(by, value).text.strip()
        except NoSuchElementException:
            return None

    def split_address(self, full_address):
        """Split the address into components: Address, City, State, Zip."""
        if not full_address:
            return None, None, None, None

        try:
            # Match address with regex
            match = re.match(r"^(.*?),\s*(.*?),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)$", full_address)
            if match:
                address, city, state, zip_code = match.groups()
                return address, city, state, zip_code
            else:
                # Fallback if address doesn't match the expected format
                parts = full_address.split(", ")
                if len(parts) >= 3:
                    address = parts[0]
                    city = parts[1]
                    state_zip = parts[2].split(" ")
                    state = state_zip[0] if len(state_zip) > 0 else None
                    zip_code = state_zip[1] if len(state_zip) > 1 else None
                    return address, city, state, zip_code
        except Exception as e:
            print(f"Error splitting address: {e}")
            return None, None, None, None

    def start_scraping(self):
        """Main method to scrape all domains."""
        try:
            domains = self.get_domains_from_csv()
            for index, domain in enumerate(domains):
                print(f"Processing ({index + 1}/{len(domains)}): {domain}")
                self.scrape_google_maps(domain)
            self.driver.quit()
        except Exception as e:
            print(f"Error during scraping process: {e}")
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    input_csv = "domains.csv"  # Input file with domains
    output_csv = "output.csv"  # Output file for results
    scraper = GeneralizedScraper(input_csv, output_csv)
    scraper.start_scraping()
