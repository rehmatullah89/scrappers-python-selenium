import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlesearch import search

# File paths
domains_file = "domains.csv"  # Ensure this file exists with proper formatting
output_file = "scraped_data.csv"

# Define the fields to scrape
fields = ["Company", "Address", "City", "State", "Zip", "CompanyDomain", "EmployeeSize", "AnnualRevenue"]

# Create an empty list to store scraped data
scraped_data = []

def scrape_website(domain):
    """Scrape the website for the desired fields."""
    data = {field: None for field in fields}  # Initialize fields with None
    data["CompanyDomain"] = domain

    try:
        # Perform a Google search to locate relevant pages
        query = f"{domain} contact us"
        search_results = search(query, num_results=3)

        for url in search_results:
            # Make an HTTP request to fetch the page content
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # Scrape relevant information (example logic, refine as needed)
            company_name = soup.find("meta", {"property": "og:site_name"}) or soup.title
            if company_name:
                data["Company"] = company_name.get("content") if company_name.name == "meta" else company_name.text.strip()

            address = soup.find("address")
            if address:
                data["Address"] = address.text.strip()

            # Break if the required data is mostly filled
            if all(data.values()):
                break
    except Exception as e:
        print(f"Error scraping {domain}: {e}")
    
    return data

try:
    # Load the CSV file
    df = pd.read_csv(domains_file)

    # Check if the 'Domain' column exists
    if "Domain" in df.columns:
        domains = df["Domain"]
    else:
        print("CSV file does not have a 'Domain' column. Please ensure it exists.")
        exit(1)

    # Scrape each domain
    for domain in domains:
        print(f"Scraping: {domain}")
        result = scrape_website(domain)
        scraped_data.append(result)

    # Save the data to a CSV file
    df_output = pd.DataFrame(scraped_data)
    df_output.to_csv(output_file, index=False)

    print(f"Scraping completed. Results saved to {output_file}.")

except FileNotFoundError:
    print(f"File {domains_file} not found. Please check the file path.")
except Exception as e:
    print(f"Error: {e}")
