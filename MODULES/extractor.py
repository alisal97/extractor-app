import re
from transformers import pipeline  
import config
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification
import phonenumbers



def extract_company_name(url):
    company_name_regex = r'www\.([a-zA-Z0-9-]+)\.(eu|it|com|net|org|gov|edu|info|biz|co)'
    match = re.search(company_name_regex, url)
    if match:
        return match.group(1)
    else:
        return None
    
def extract_email(content):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(email_regex, content)
    return emails

def extract_locations(text):
    tokenizer = AutoTokenizer.from_pretrained("ml6team/bert-base-uncased-city-country-ner")
    model = AutoModelForTokenClassification.from_pretrained("ml6team/bert-base-uncased-city-country-ner")
    nlp = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    chunks = [text[i:i+256] for i in range(0, len(text), 512)]
    
    unique_cities = set()
    for chunk in chunks:
        output = nlp(chunk)
        city = ""
        for entity in output:
            if entity['entity_group'] == "CITY" and entity['score'] >= 0.978:
                city = entity['word']
                unique_cities.add(city)
    return list(unique_cities)

def extract_phone_numbers(content):
    phone_numbers = []

    for match in phonenumbers.PhoneNumberMatcher(content, "IT"):
        phone_number = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        phone_numbers.append(phone_number)

    if phone_numbers:
        return phone_numbers
    else:
        return None


def extract_sector(content):
    tokenizer = AutoTokenizer.from_pretrained("MKaan/multilingual-cpv-sector-classifier")
    model = AutoModelForSequenceClassification.from_pretrained("MKaan/multilingual-cpv-sector-classifier")

    chunk_size = 512
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

    max_accuracy = -1
    predicted_sector = 'Unknown'

    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        logits = outputs.logits

        predicted_label_index = logits.argmax().item()

        confidence_score = torch.softmax(logits, dim=1)[0][predicted_label_index].item()

        if confidence_score > max_accuracy:
            max_accuracy = confidence_score

            label_mapping = config.sector_labels
            predicted_sector = label_mapping.get(predicted_label_index, 'Unknown')

    return predicted_sector



def extract_social_media_links(content, url):
    social_media_links = set()
    company_name = extract_company_name(url)
    pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+/[-\w./?=&]+'
    matches = re.findall(pattern, content)
    if company_name != None: 
        for match in matches:
            if 'facebook.com' in match or 'linkedin.com' in match or 'instagram.com' in match:
                if company_name.lower() in match.lower():
                    social_media_links.add(match)
    else: 
        for match in matches:
            if 'facebook.com' in match or 'linkedin.com' in match or 'instagram.com' in match:
                social_media_links.add(match)
    return list(social_media_links)

def extractor(scraped_content, url):
    extracted_info = {
        config.emails: extract_email(scraped_content) or [],
        config.locations: extract_locations(scraped_content),
        config.phone_number: extract_phone_numbers(scraped_content) or [],
        config.socials: set(extract_social_media_links(scraped_content, url)),
    }
    return extracted_info
