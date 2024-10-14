import requests
from bs4 import BeautifulSoup
import os
import csv

 
def scrape_anercea_eleveurs():
    website_name = "anercea"
    url = "https://anercea.com/annuaire-des-eleveurs-de-reines-apiculture/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    all_data = []

    # Send a GET request to fetch the page content
    response = requests.get(url, headers=headers)

    # Check for a successful response
    if response.status_code != 200:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the elements containing information for each eleveur
    eleveur_list = soup.find_all('div', class_='jet-listing-grid__item')
    save_html_to_file(eleveur_list)
    for element in eleveur_list:
        # Extract the name
        name_tag = element.find('h3', class_='jet-listing-dynamic-field__content')
        name = name_tag.get_text(strip=True) if name_tag else 'N/A'

        # Extract the phone number (Check for different selector)
        phone_tag = element.find('div', class_='jet-listing-dynamic-field__inline-wrap')
        phone = phone_tag.get_text(strip=True).replace(' ', '') if phone_tag else 'N/A'

        # Extract the selection info (Check for different selector)
        selection_tag = element.find('div', class_='jet-listing-dynamic-field__content')
        selection = selection_tag.get_text(strip=True) if selection_tag else 'N/A'

        # Deduplicate by checking if this entry already exists in all_data
        if any(d['Name'] == name and d['Phone'] == phone for d in all_data):
            continue  # Skip adding this data if it's already present

        # Append the extracted data to all_data list
        all_data.append({
            'Name': name,
            'Phone': phone,
            'Selection': selection
        })

    # Save the collected data into a CSV file
    save_to_csv(all_data, website_name)
    
    return all_data


def save_to_csv(data_list, website_name):
    csv_file = f"{website_name}.csv"
    headers = ['Name', 'Phone', 'Selection']
 # Check if file exists and remove it if so
    checkFile(csv_file)
    # Check if the CSV file already exists
    file_exists = os.path.exists(csv_file)

    # Open the file in append mode to add data
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        # Write headers only if the file doesn't already exist
        if not file_exists:
            writer.writeheader()

        # Write the data to the CSV file
        writer.writerows(data_list)

    print(f"Data saved to {csv_file}")

def checkFile(filename):
     # Check if file exists and remove it if so
    if os.path.exists(filename):
        os.remove(filename)
        print(f"Existing file {filename} has been deleted.")

def save_html_to_file(soup, filename="page_content.html"):
    # Check if file exists and remove it if so
    checkFile(filename)
    # Convert soup object to string and write it to a new HTML file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print(f"HTML content saved to {filename}")



