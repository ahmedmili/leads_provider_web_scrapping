from flask import Blueprint, request, jsonify,send_file
from .scrappers.charolais71 import scrape_charolais71
from .scrappers.anercea import scrape_anercea_eleveurs
from .scrappers.capgenes import scrape_capgenes


import requests
from pdfminer.high_level import extract_text
import xml.etree.ElementTree as ET
import io



scraper_bp = Blueprint('scraper', __name__)

@scraper_bp.route('/scrape/charolais71', methods=['GET'])
def scrapeCharolais71():
    # Call the web scraping function from scraper.py
    result = scrape_charolais71()

    return jsonify(result)


@scraper_bp.route('/scrape/anercea', methods=['GET'])
def scrapeAnercea():
    # Call the web scraping function from charolais71.py
    result = scrape_anercea_eleveurs()

    return jsonify(result)

@scraper_bp.route('/scrape/capgenes', methods=['GET'])
def scrapeCapgenes():
    # Call the web scraping function from anercea.py
    result = scrape_capgenes()

    return jsonify(result)


@scraper_bp.route('/convert_pdf_to_xml', methods=['GET'])
def convert_pdf_to_xml():
    pdf_url = "https://www.capgenes.com/wp-content/uploads/2024/02/Annuaire_2024_Capgenes_1701_WEB.pdf"

    if not pdf_url:
        return jsonify({"error": "pdf_url parameter is required"}), 400

    # Fetch the PDF from the URL
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400

    # Extract text from the PDF
    try:
        pdf_text = extract_text(io.BytesIO(response.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Convert text to XML
    xml_file = convert_text_to_xml(pdf_text)

    # Send the XML file as a response
    return send_file(
        xml_file,
        as_attachment=True,
        download_name="converted_file.xml",
        mimetype="application/xml"
    )


# Helper function to convert text to XML format
def convert_text_to_xml(text):
    root = ET.Element("document")
    body = ET.SubElement(root, "body")
    # Split text into lines and add each as a separate element
    for line in text.splitlines():
        paragraph = ET.SubElement(body, "paragraph")
        paragraph.text = line
    tree = ET.ElementTree(root)
    xml_bytes = io.BytesIO()
    tree.write(xml_bytes, encoding="utf-8", xml_declaration=True)
    xml_bytes.seek(0)
    return xml_bytes