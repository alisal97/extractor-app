from flask import Flask, json, request, jsonify
import requests
import config
from collections import defaultdict
from MODULES.extractor import extractor, extract_company_name, extract_sector
app = Flask(__name__)

scraper = config.scraper_app


@app.route('/extractor-app', methods=['POST'])
def get_info():
    data = request.json
    app.logger.info(f"Received data: {data}")
    
    if not data or 'urls' not in data:
        return jsonify({'error': 'No URLs provided'}), 400

    consolidated_results = defaultdict(dict)
    for url in data['urls']:
        response = requests.post(scraper, json={'urls': [url]})
        
        if response.status_code == 200:
            scraped_data_list = response.json()
            for scraped_data in scraped_data_list:
                content = scraped_data.get('content')
                content = str(content)  
                if content:
                    company_name = extract_company_name(scraped_data['url']) 
                    sector = extract_sector(content)
                    profile_data = extractor(content)

                    if 'E-mails' not in consolidated_results[url]:
                        consolidated_results[url]['E-mails'] = set()
                    consolidated_results[url]['E-mails'].update(profile_data.get(config.emails, []))

                    if 'Social Media Links' not in consolidated_results[url]:
                        consolidated_results[url]['Social Media Links'] = set()
                    consolidated_results[url]['Social Media Links'].update(profile_data.get(config.socials, []))

                    if 'Phone Numbers' not in consolidated_results[url]:
                        consolidated_results[url]['Phone Numbers'] = set()
                    consolidated_results[url]['Phone Numbers'].update(profile_data.get(config.phone_number, []))

                    if 'Locations' not in consolidated_results[url]:
                        consolidated_results[url]['Locations'] = set()
                    consolidated_results[url]['Locations'].update(profile_data.get(config.locations, []))


                    consolidated_results[url].setdefault(config.name, company_name)
                    consolidated_results[url].setdefault(config.sector, sector)
                else:
                    app.logger.warning("Content not found in scraped data")
        else:
            app.logger.error(f"Error from scraper service. Status Code: {response.status_code}, Content: {response.text}")
            return jsonify({'error': 'Error from scraper service'}), response.status_code
        
    for url, data in consolidated_results.items():
        if 'E-mails' in data:
            data['E-mails'] = list(data['E-mails'])
        if 'Social Media Links' in data:
            data['Social Media Links'] = list(data['Social Media Links'])
        if 'Phone Numbers' in data:
            data['Phone Numbers'] = list(data['Phone Numbers'])
        if 'Locations' in data:
            data['Locations'] = list(data['Locations'])
            
    results_list = [{'url': url, **data} for url, data in consolidated_results.items()]
    return jsonify(results_list), 200

if __name__ == '__main__':
    app.run(debug=True, port=config.port)
