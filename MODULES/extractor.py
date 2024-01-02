import re
from transformers import pipeline  
import config
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def extract_email(content):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_regex, content)
    return emails


def extract_office_locations(content):
    pattern = re.compile(r'\b\d{1,5}\s+[\w\s]+\b,\s*[\w\s]+\b,\s*\d{5}\s*[\w\s]+\b|\b\d{1,5}\s+[\w\s]+\b,\s*\d{5}\b')

    matches = re.findall(pattern, content)

    return matches

def extract_phone_numbers(content):
    phone_regex = r'\b(?:\+\d{1,2}\s?)?(?:(?:\(\d{1,4}\))|(?:\d{1,4}))[-.\s]?\d{1,12}\b'
    phone_numbers = re.findall(phone_regex, content)
    return phone_numbers

def extract_sector(content): #company type
    tokenizer = AutoTokenizer.from_pretrained("MKaan/multilingual-cpv-sector-classifier")
    model = AutoModelForSequenceClassification.from_pretrained("MKaan/multilingual-cpv-sector-classifier")

    inputs = tokenizer(content, return_tensors="pt", truncation=True)

    # Make predictions
    outputs = model(**inputs)
    logits = outputs.logits

    # Get the predicted label index
    predicted_label_index = logits.argmax().item()

    # Map the label index to the actual sector (modify as needed)
    label_mapping = config.sector_labels

    detected_sector = label_mapping.get(predicted_label_index, 'Unknown')

    return detected_sector

def extract_company_name(url):
    company_name_regex = r'www\.([a-zA-Z0-9-]+)\.(com|net|org|gov|edu|info|biz|co)'
    match = re.search(company_name_regex, url)
    if match:
        return match.group(1)
    else:
        return None

def extract_social_media_links(content):
    social_media_regex = (
        r'https?://(?:www\.)?(?:facebook|twitter|instagram|linkedin)\.com/[a-zA-Z0-9_]+/?'
    )
    links = re.findall(social_media_regex, content)
    return links

def extractor(scraped_content):
    extracted_info = {
        config.emails: extract_email(scraped_content),
        config.locations: extract_office_locations(scraped_content),
        config.phone_number: extract_phone_numbers(scraped_content),
        config.sector: extract_sector(scraped_content),
        config.socials: extract_social_media_links(scraped_content),
    }
    return extracted_info
