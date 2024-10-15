import os
import io
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import csv
import re


PDF_URL = "https://www.capgenes.com/wp-content/uploads/2024/02/Annuaire_2024_Capgenes_1701_WEB.pdf"

def extract_pages_from_html(filename="full_pdf_content.html", pages=[6, 7]):
    with open(filename, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    extracted_data = []
    for page in pages:
        page_header = soup.find('h2', text=f'Page {page}')
        if page_header:
            # Find the corresponding paragraph with page content
            page_content = page_header.find_next('div')
            if page_content:
                extracted_data.append({
                    "Page": page,
                    "Content": page_content.get_text(separator="\n")
                })
            else:
                print(f"Warning: No content found for page {page}")
        else:
            print(f"Warning: Page {page} not found in the HTML")

    return extracted_data


# Function to save the entire PDF as HTML with styles
def save_pdf_as_html(pdf_file, filename="full_pdf_content.html"):
    html_content = "<html><body>"
    
    # Open the PDF using PyMuPDF with the BytesIO object
    doc = fitz.open(stream=pdf_file, filetype="pdf")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        
        # Start a new section for each page
        html_content += f"<h2>Page {page_num + 1}</h2>"
        
        for block in blocks:
            if "lines" in block:
                # Generate block level div with boundary
                block_style = f"border: 1px solid black; margin: 10px; padding: 10px;"
                html_content += f"<div style='{block_style}'>"
                
                # Process lines and spans (text fragments)
                for line in block["lines"]:
                    for span in line["spans"]:
                        color = "#{:06x}".format(span["color"])  # Get text color in hex
                        text = span["text"].replace("\n", "<br>")  # Replace newlines with <br>
                        font_size = span["size"]  # Font size
                        # Add span with style for text color and font size
                        html_content += f"<span style='color:{color}; font-size:{font_size}px;'>{text}</span>"
                
                html_content += "</div>"  # End block

    html_content += "</body></html>"

    # Save to file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"Full PDF content saved to {filename}")

# Function to fetch the PDF from a URL
def fetch_pdf_from_url(pdf_url):
    response = requests.get(pdf_url)
    response.raise_for_status()  # Raise an exception if the request was unsuccessful
    return io.BytesIO(response.content)

# Function to extract text from specific pages (6 and 7)
def process_extracted_data(extracted_data):
    formatted_data = []

    for entry in extracted_data:
        content = entry["Content"]
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Try identifying headers by their text or another tag type (like <h2> or <p>)
        # Adjust this based on the actual content you see
        association_headers = soup.find_all(['h2', 'p', 'span'])

        for header in association_headers:
            header_text = header.get_text(strip=True)
            
            # Check if the header text looks like an association name (e.g., by checking for keywords or length)
            if "Association" in header_text or len(header_text.split()) > 1:  # Example check, adjust as necessary
                association = header_text

                # Find the following divs with association details
                details_divs = header.find_next_siblings('div')
                
                # Initialize placeholders for details
                association_data = {
                    "association": association,
                    "type": None,
                    "president": None,
                    "animatrice": None,
                    "phone": None,
                    "email": None,
                    "website": None,
                    "breeders": None,
                    "animals": None
                }

                # Iterate through the details divs
                for div in details_divs:
                    div_text = div.text.strip()
                    
                    # Parsing type of association
                    if "Président" in div_text:
                        association_data["president"] = div_text.split("Président :")[1].strip()
                    
                    if "Animatrice" in div_text or "Animateur" in div_text:
                        association_data["animatrice"] = div_text.split("Animatrice :")[1].strip() if "Animatrice" in div_text else div_text.split("Animateur :")[1].strip()
                    
                    # Extracting phone
                    if "B " in div_text:
                        association_data["phone"] = div_text.split("B ")[1].split()[0].strip()
                    
                    # Extracting email
                    if "C " in div_text:
                        association_data["email"] = div_text.split("C ")[1].split()[0].strip()
                    
                    # Extracting website
                    if ".com" in div_text or ".org" in div_text:
                        association_data["website"] = div_text.split()[-1].strip()
                    
                    # Extracting breeders and animals
                    if "éleveurs" in div_text:
                        breeders = [int(s) for s in div_text.split() if s.isdigit()]
                        if len(breeders) == 2:
                            association_data["breeders"] = breeders[0]
                            association_data["animals"] = breeders[1]
                
                # Add the parsed data to the formatted data list
                formatted_data.append(association_data)
    
    return formatted_data

def extract_association_names(text):
    # A basic pattern that could match typical association names (adjust the pattern as needed)
    pattern = re.compile(r"\bAssociation\b.*")  
    return pattern.findall(text)

def process_extracted_data(extracted_data):
    formatted_data = []

    for entry in extracted_data:
        content = entry["Content"]
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Identify blocks by association names
        association_headers = soup.find_all('span', style="color: #ffffff; font-size: 13px")
        
        for header in association_headers:
            association = header.text.strip()
            
            # Find the following divs with association details
            details_divs = header.find_next_siblings('div')
            # Initialize placeholders for details
            association_data = {
                "association": association,
                "type": None,
                "president": None,
                "animatrice": None,
                "phone": None,
                "email": None,
                "website": None,
                "breeders": None,
                "animals": None
            }

            # Iterate through the details divs
            for div in details_divs:
                div_text = div.text.strip()
                
                # Parsing type of association
                if "Président" in div_text:
                    association_data["president"] = div_text.split("Président :")[1].strip()
                
                if "Animatrice" in div_text or "Animateur" in div_text:
                    association_data["animatrice"] = div_text.split("Animatrice :")[1].strip() if "Animatrice" in div_text else div_text.split("Animateur :")[1].strip()
                
                # Extracting phone
                if "B " in div_text:
                    association_data["phone"] = div_text.split("B ")[1].split()[0].strip()
                
                # Extracting email
                if "C " in div_text:
                    association_data["email"] = div_text.split("C ")[1].split()[0].strip()
                
                # Extracting website
                if ".com" in div_text or ".org" in div_text:
                    association_data["website"] = div_text.split()[-1].strip()
                
                # Extracting breeders and animals
                if "éleveurs" in div_text:
                    breeders = [int(s) for s in div_text.split() if s.isdigit()]
                    if len(breeders) == 2:
                        association_data["breeders"] = breeders[0]
                        association_data["animals"] = breeders[1]
            
            # Add the parsed data to the formatted data list
            formatted_data.append(association_data)
    
    return formatted_data
# Function to save data to a CSV file
def save_data_to_csv(data, filename="extracted_data.csv"):
    headers = ["name", "description", "Présidentes", "phone", "email", "website", "aneca_1", "capgènes_1", "aneca_2", "capgènes_2"]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    
    print(f"Data saved to {filename}")

# Main scraping controller function
def scrape_capgenes():
    try:
        pdf_file = fetch_pdf_from_url(PDF_URL)
        save_pdf_as_html(pdf_file)
        extracted_data = extract_pages_from_html(pages=[6, 7])
        processed_data = process_extracted_data(extracted_data)
        save_data_to_csv(processed_data)
        return processed_data
    except Exception as e:
        print(f"Error: {e}")
        raise e
