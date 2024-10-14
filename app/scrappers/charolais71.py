import requests
from bs4 import BeautifulSoup
import csv
import time
import os




def scrape_charolais71():
    website_name = "charolais71"
    i = 1  # Start from the first page
    all_data = []
    all_seen_eleveurs = set()  # To track unique Eleveur Numbers

    while True:
        print(f"Scraping page {i}...")
        url = f'https://www.charolais71.fr/annuaire-des-eleveurs.html?rech_eleveur=1&page={i}'

        # Adding a delay to avoid too many requests
        time.sleep(2)  # Wait for 2 seconds before each request

        response = requests.get(url)

        if response.status_code == 429:
            # If we get a "Too Many Requests" error, wait and retry
            print(f"Rate limit hit. Waiting 60 seconds before retrying...")
            time.sleep(60)  # Wait 60 seconds before retrying
            continue  # Retry the request

        if response.status_code != 200:
            print(f"Failed to retrieve page {i}. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the specific <ul> with id 'aff_eleveur'
        ul_element = soup.find('ul', id='aff_eleveur')

        if not ul_element:
            # No more data on this page (last page or no data found)
            print(f"No more data on page {i}, stopping.")
            break

        # Check if the <ul> has any <li> elements
        li_elements = ul_element.find_all('li')

        if not li_elements:
            # If no <li> elements are found, it indicates that we've reached the last page
            print(f"Page {i} has no data, stopping scraping.")
            break

        # Fetch data from the current page
        page_data = fetch_charolais71_data(ul_element)

        # Filter the data to remove duplicates and add new entries
        for entry in page_data:
            if entry['Eleveur Number'] not in all_seen_eleveurs:
                all_data.append(entry)
                all_seen_eleveurs.add(entry['Eleveur Number'])  # Mark as seen
            else:
                # If the data already exists, we stop scraping
                print(f"Duplicate found for Eleveur Number {entry['Eleveur Number']}, stopping.")
                save_to_csv(all_data, website_name)  # Save before stopping
                return all_data  # Stop and return data

        # Increment the page number to get the next page
        i += 1

    # Save the data after scraping all pages
    save_to_csv(all_data, website_name)

    print(f"Scraping complete. Total pages scraped: {i-1}")
    return all_data




def fetch_charolais71_data(ul_element):
    data_list = []

    # Extract data from the <li> elements as per your earlier logic
    for li in ul_element.find_all('li'):
        name = li.find('h2').get_text(strip=True) if li.find('h2') else ''
        business_name = li.find('h4').get_text(strip=True) if li.find('h4') else ''
        eleveur_number = li.find('h3').get_text(strip=True).replace("N° Eleveur : ", "") if li.find('h3') else ''
        address = li.find('p').get_text(strip=True) if li.find('p') else ''

        phone_span = li.find_all('span')
        phone = phone_span[0].get_text(strip=True).replace("Tél : ", "") if len(phone_span) > 0 else ''
        mobile = phone_span[1].get_text(strip=True).replace("Mobile : ", "") if len(phone_span) > 1 else ''

        email_element = li.find('span', class_='mel2')
        email = email_element.get_text(strip=True) if email_element else ''

        # Append to data list
        data_list.append({
            'Name': name,
            'Business Name': business_name,
            'Eleveur Number': eleveur_number,
            'Address': address,
            'Phone': phone,
            'Mobile': mobile,
            'Email': email
        })

    return data_list

    


def save_to_csv(data_list, website_name):
    csv_file = f"{website_name}.csv"
    headers = ['Name', 'Business Name', 'Eleveur Number', 'Address', 'Phone', 'Mobile', 'Email']

    # Check if the CSV file already exists
    file_exists = os.path.exists(csv_file)

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        if not file_exists:
            # If file doesn't exist, write headers
            writer.writeheader()

        # Write the data to the CSV file (append mode)
        writer.writerows(data_list)

    print(f"Data saved to {csv_file}")



