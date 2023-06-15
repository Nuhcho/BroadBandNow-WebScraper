import re
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define the URLs for different categories
urlList = {
    "5G Home Internet": "https://broadbandnow.com/5G/home-internet",
    "Fiber Providers": "https://broadbandnow.com/Fiber-Providers",
    "Cable Providers": "https://broadbandnow.com/Cable-Providers",
    "Fixed Wireless Providers": "https://broadbandnow.com/Fixed-Wireless-Providers",
    "Satellite Providers": "https://broadbandnow.com/Satellite-Providers",
    "DSL Providers": "https://broadbandnow.com/DSL-Providers"
}

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--ignore-certificate-errors")  # Ignore certificate errors
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--disable-javascript")

# Initialize the webdriver with Chrome options
browser = webdriver.Chrome(options=chrome_options)

# Dictionary to store the results
result = {}

# Iterate over each category and corresponding URL
for category, url in urlList.items():
    # Visit the URL
    browser.get(url)

    # Find all <a> elements on the page
    links = browser.find_elements(By.TAG_NAME, "a")

    # Set to store the URLs
    urlSet = {url}

    # Filter and extract relevant URLs
    for link in links:
        href = link.get_attribute("href")
        if href and "page" in href:
            urlSet.add(href)

    # Set to store the extracted sites
    sites = set()

    # Visit each URL and extract site URLs
    for url in urlSet:
        browser.get(url)
        tbody_elements = browser.find_elements(By.TAG_NAME, "tbody")
        for tbody in tbody_elements:
            links_in_tbody = tbody.find_elements(By.TAG_NAME, "a")
            for link in links_in_tbody:
                href = link.get_attribute("href")
                if href:
                    sites.add(href)

    # Store the sites for the category
    result[category] = sites

# Dictionary to store the nested results
nested_result = {}

# Iterate over each category and sites
for category, sites in result.items():
    # Dictionary to store nested values for each site
    nested_dict = {}
    for site in sites:
        # Visit the site URL
        browser.get(site)

        # Wait for the page to load
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "title")))

        # Extract cost match using regex
        regex_pattern = r'\$\d+'
        costMatch = list(set(re.findall(regex_pattern, browser.page_source)))  # Use set to remove duplicates

        # If there is no cost detected
        if len(costMatch) == 0:
            costMatch = "None"

        # Extract internet speed using regex
        speed_pattern = r'\d+\s?(?:[KMGkmg]bps)'
        speedMatch = list(set(re.findall(speed_pattern, browser.page_source)))  # Use set to remove duplicates

        # Extract service areas using div elements
        serviceAreas = []
        for divElement in browser.find_elements(By.CSS_SELECTOR, "div.city-data__city-population"):
            city_name = divElement.text.split("\n")[0].strip()
            population = ""
            h4_element = divElement.find_elements(By.TAG_NAME, "h4")
            if len(h4_element) > 0:
                population = h4_element[0].text.strip()
            serviceAreas.append({"City": city_name, "Population": population})
        # Checks if nothing was returned and then grabs the location from the table link
        if len(serviceAreas) == 0:
            serviceAreas.append("None")

        # Extract the name match from the title tag
        nameResult = browser.find_element(By.TAG_NAME, "title").get_attribute("textContent").split(" : ")[0].strip()
        nameResult = nameResult.split(" | ")[0].strip()

        # Store the extracted values in the nested dictionary
        nested_dict[site] = {
            "Cost Match": costMatch,
            "Internet Speed": speedMatch,
            "Name Match": nameResult,
            "Service Areas": serviceAreas
        }

    # Store the nested dictionary for the category
    nested_result[category] = nested_dict

# Close the browser
browser.quit()


# Creates the CSV file
with open("searchWordCount.csv", "w", newline="") as searchWordCount:
    writer = csv.writer(searchWordCount, delimiter=' ')
    writer.writerow(["Site ", "Name Match ", "Cost Match ", "Internet Speed ", "City or Stat ", "Population ", "Type"])
    for category, nested_dict in nested_result.items():
        for site, values in nested_dict.items():
            writer.writerow([site, values['Name Match'], values['Cost Match'], values['Internet Speed'],
                                 values["Service Areas"], category])