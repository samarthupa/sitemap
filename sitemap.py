import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to check status code and redirection of URL
def check_status_and_redirection(url):
    try:
        response = requests.get(url, allow_redirects=False)
        status_code = response.status_code
        redirection_url = response.headers.get('location')
        if status_code in [301, 307, 302] and redirection_url:
            return status_code, redirection_url
        else:
            return status_code, "N/A"
    except Exception as e:
        return str(e), "N/A"

# Function to extract text using XPath
def extract_text(url, xpath):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.select(xpath)
        if elements:
            return elements[0].text.strip()
        else:
            return "N/A"
    except:
        return "N/A"

# Streamlit UI
st.title("URL Analysis Tool")

# Input fields
urls = st.text_area("Enter URL(s) (one URL per line)", height=150)
user_agents = st.selectbox("Choose User Agent", ["Chrome", "Firefox", "Safari"])
xpath = st.text_input("Enter XPath to Extract Text")

if st.button("Submit"):
    urls_list = urls.split('\n')
    results = []
    for url in urls_list:
        headers = {"User-Agent": user_agents}
        status_code, redirection_url = check_status_and_redirection(url)
        extracted_text = extract_text(url, xpath) if xpath else "N/A"
        results.append((url, status_code, redirection_url, extracted_text))
    
    # Display results in table
    st.table(results)
