from flask import Blueprint, request, jsonify
from .scrappers.charolais71 import scrape_charolais71
from .scrappers.anercea import scrape_anercea_eleveurs

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

@scraper_bp.route('/scrape/test', methods=['GET'])
def test():
    # Call the web scraping function from anercea.py
    result = scrape_anercea_eleveurs()

    return jsonify(result)
