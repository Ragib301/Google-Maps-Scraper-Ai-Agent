import re
import base64
import json
import streamlit as st
from google import genai
from secretKey import gemini_api

client = genai.Client(api_key=gemini_api)
model = "gemini-2.0-flash"


@st.cache_data
def enhance_data(scraped_data):
    st.write('Enhancing data using Gemini API...')
    prompt = f"""
    I have given you a JSON data, which contains scraped business information from 
    Google Maps. You can see many of the comapany emails are missing. Your task is 
    to fillup the blank emails by searching for the company. The company name, address 
    and website are given. Only return the completed data in json format, nothing else 
    should be printed. If you are unable to search, then simply fillup using sample emails, 
    make sure your given email looks familiar. You will also see some of the emails are crooked
    or temporary mail or they are like user@domain.org. Make sure to replace them. Again, just 
    only return the JSON data.
    
    Scraped Google Maps JSON data:
    {str(scraped_data)}
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        match = re.search(r'\[\s*{.*?}\s*\]', response.text, re.DOTALL)
        data = json.loads(match.group(0))
        return data

    except Exception as e:
        return str(e)


def remove_duplicates(scraped_data):
    st.write('Remvoing duplicates...')
    seen_names = set()
    seen_websites = set()
    seen_emails = set()
    unique_data = []

    for entry in scraped_data:
        name = entry.get("name", "").strip().lower()
        website = entry.get("website", "").strip().lower()
        emails = [e.strip().lower() for e in entry.get("emails", [])]

        is_duplicate = (
            name in seen_names or
            website in seen_websites or
            any(email in seen_emails for email in emails)
        )

        if not is_duplicate:
            unique_data.append(entry)
            seen_names.add(name)
            seen_websites.add(website)
            seen_emails.update(emails)

    return unique_data


@st.cache_data
def set_background(image_file):
    with open(image_file, "rb") as f:
        img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        style = f"""
            <style>
            .stApp {{
                background-image: url(data:image/png;base64,{b64_encoded});
                background-size: cover;
            }}
            </style>
        """
        st.markdown(style, unsafe_allow_html=True)
