from flask import Flask, json, request, jsonify
import requests
import config
from MODULES.extractor import extractor
app = Flask(__name__)

scraper = config.scraper_app

@app.route('/extractor-app', methods=['POST'])
def app():
    data = request.json
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    scraper_url = config.scraper_app
    response = requests.post(scraper_url, json={'url': data['url']})

    if response.status_code == 200:
        scraped_data = response.json()
        results = [extractor(page['text']) for page in scraped_data]
        return jsonify(results), 200
    else:
        return jsonify({'error': 'Error from scraper service'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=config.port) 