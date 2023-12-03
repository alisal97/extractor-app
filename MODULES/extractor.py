import re
from transformers import pipeline  
import config

def extract_email(content):
    email_regex = r"+"
    emails = re.findall(email_regex, content)
    return emails

def extract_office_locations(content):
    pass

def extract_phone_numbers(content):
    phone_regex = r""
    phone_numbers = re.findall(phone_regex, content)
    return phone_numbers

def extract_company_profile(content): #company type
    pass

def extract_social_media_links(content):
    pass

def extract_ceo_name(content):
    pass

def extractor(scraped_content):
    extracted_info = {
        config.emails: extract_email(scraped_content),
        config.locations: extract_office_locations(scraped_content),
        config.phone_number: extract_phone_numbers(scraped_content),
        config.name: extract_company_profile(scraped_content),
        config.profile: "", 
        config.sector: "",
        config.socials: extract_social_media_links(scraped_content),
        config.ceo: extract_ceo_name(scraped_content)
    }
    return extracted_info
