from flask import Flask, json, request, jsonify
import requests
import config
from MODULES.extractor import extractor, extract_company_name
app = Flask(__name__)

scraper = config.scraper_app

@app.route('/extractor-app', methods=['POST'])
def get_info():
    data = request.json
    if not data or 'urls' not in data:
        return jsonify({'error': 'No URLs provided'}), 400

    results = []
    for url in data['urls']:
        response = requests.post(scraper, json={'url': url})
        
        if response.status_code == 200:
            scraped_data = response.json()
            scraped_url = scraped_data['url']
            result = {
                config.name: extract_company_name(scraped_url[0]),
                config.profile: extractor(scraped_data)
            }
            results.append(result)
        else:
            return jsonify({'error': 'Error from scraper service'}), response.status_code

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True, port=config.port)
