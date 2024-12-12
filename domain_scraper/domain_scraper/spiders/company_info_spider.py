import scrapy
import csv

class CompanyInfoSpider(scrapy.Spider):
    name = 'company_info'

    # Define the output CSV file and initialize it with headers
    output_file = 'output.csv'

    def __init__(self, *args, **kwargs):
        super(CompanyInfoSpider, self).__init__(*args, **kwargs)
        # Open the CSV file in write mode and write the header
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Company', 'Address', 'City', 'State', 'Zip', 'CompanyDomain', 'EmployeeSize', 'AnnualRevenue'])

    # Read domains from CSV file and generate start URLs
    def start_requests(self):
        with open('domains.csv', 'r') as file:
            reader = csv.reader(file)
            # Skip header row
            next(reader)
            for row in reader:
                domain = row[0]
                url = f"https://{domain}"
                yield scrapy.Request(url=url, callback=self.parse, meta={'domain': domain})

    def parse(self, response):
        domain = response.meta['domain']
        
        # Extracting data using CSS selectors
        company = response.css('meta[name="company"]::attr(content)').get(default='N/A')
        address = response.css('meta[name="address"]::attr(content)').get(default='N/A')
        city = response.css('meta[name="city"]::attr(content)').get(default='N/A')
        state = response.css('meta[name="state"]::attr(content)').get(default='N/A')
        zip_code = response.css('meta[name="zip"]::attr(content)').get(default='N/A')
        employee_size = response.css('meta[name="employee-size"]::attr(content)').get(default='N/A')
        annual_revenue = response.css('meta[name="annual-revenue"]::attr(content)').get(default='N/A')

        # Save data to output CSV file
        with open(self.output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([company, address, city, state, zip_code, domain, employee_size, annual_revenue])
