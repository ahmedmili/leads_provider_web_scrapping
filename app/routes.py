from flask import Blueprint, request, jsonify
from .scraper import scrape_charolais71

scraper_bp = Blueprint('scraper', __name__)

@scraper_bp.route('/scrape/charolais71', methods=['GET'])
def scrape():
    # Call the web scraping function from scraper.py
    result = scrape_charolais71()

    return jsonify(result)
