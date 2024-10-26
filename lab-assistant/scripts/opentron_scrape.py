import requests
from bs4 import BeautifulSoup
import os
import argparse

# Base URL and default storage directory
DEFAULT_BASE_URL = "https://protocols.opentrons.com"
DEFAULT_STORAGE_PATH = "data/"

# Function to save text to a file in the specified path
def save_text_to_file(protocol_name, content, storage_path):
    # Ensure the storage directory exists
    os.makedirs(storage_path, exist_ok=True)
    
    filename = os.path.join(storage_path, f"{protocol_name}.txt")
    # Create the file and write the content
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Saved protocol '{protocol_name}' to {filename}")

# Function to extract protocol information from the protocol page
def extract_protocol_data(protocol_url, base_url, storage_path):
    response = requests.get(base_url + protocol_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div with the class 'selected-protocol'
    protocol_div = soup.find('div', class_='selected-protocol')
    if protocol_div:
        # Extract the text content
        protocol_content = protocol_div.get_text(separator="\n", strip=True)
        protocol_name = protocol_url.split("/")[-1]  # Use the protocol ID or name in URL for the file name
        save_text_to_file(protocol_name, protocol_content, storage_path)
    else:
        print(f"No protocol data found for {protocol_url}")

# Function to scrape protocols in each subcategory
def scrape_subcategory(subcategory_url, base_url, storage_path):
    response = requests.get(base_url + subcategory_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all protocols in the subcategory page
    protocols = soup.find_all('div', class_='protocol')
    for protocol in protocols:
        # Extract the href link for the protocol
        protocol_link = protocol.find('a', href=True)
        if protocol_link:
            protocol_url = protocol_link['href']
            extract_protocol_data(protocol_url, base_url, storage_path)

# Function to recursively navigate subcategories
def scrape_categories(base_url, storage_path):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all 'subCategory' links
    subcategories = soup.find_all('a', class_='subCategory')
    
    for subcategory in subcategories:
        subcategory_url = subcategory['href']
        print(f"Scraping subcategory: {subcategory_url}")
        scrape_subcategory(subcategory_url, base_url, storage_path)

# Main function to set up argument parsing
def main():
    parser = argparse.ArgumentParser(description="Recursive web scraper for Opentrons protocol library")
    
    # Argument for the storage path
    parser.add_argument(
        '--path', 
        type=str, 
        default=DEFAULT_STORAGE_PATH, 
        help="Path to store scraped text files (default: 'data/')"
    )
    
    # Argument for the root URL
    parser.add_argument(
        '--url', 
        type=str, 
        default=DEFAULT_BASE_URL, 
        help="Root URL to start scraping (default: 'https://protocols.opentrons.com/')"
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the scrape function with provided arguments
    scrape_categories(args.url, args.path)

if __name__ == "__main__":
    main()
