from flask import Flask, json, request, jsonify
import requests
import config
from MODULES.extractor import extractor, extract_company_name, extract_sector
app = Flask(__name__)

scraper = config.scraper_app

@app.route('/extractor-app', methods=['POST'])
def get_info():
    data = request.json
    app.logger.info(f"Received data: {data}")
    
    if not data or 'urls' not in data:
        return jsonify({'error': 'No URLs provided'}), 400

    results = []
    for url in data['urls']:
        response = requests.post(scraper, json={'urls': [url]})
        
        if response.status_code == 200:
            scraped_data_list = response.json()
            for scraped_data in scraped_data_list:
                content = scraped_data.get('content')
                content = str(content)  
                if content:
                    results.append({
                        config.name: extract_company_name(scraped_data['url']),
                        config.sector: extract_sector(content),
                        config.profile: extractor(content)
                    })
                else:
                    app.logger.warning("Content not found in scraped data")
        else:
            app.logger.error(f"Error from scraper service. Status Code: {response.status_code}, Content: {response.text}")
            return jsonify({'error': 'Error from scraper service'}), response.status_code
    return jsonify(results), 200


if __name__ == '__main__':
    app.run(debug=True, port=config.port)
