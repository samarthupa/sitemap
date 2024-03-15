import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to check status code of URL
def check_status_code(url):
    try:
        response = requests.get(url)
        return response.status_code
    except:
        return "N/A"

# Function to check redirection of URL
def check_redirection(url):
    try:
        response = requests.get(url)
        return response.history
    except:
        return "N/A"

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
check_status = st.checkbox("Check Status Code")
check_redirection = st.checkbox("Check Redirection")
xpath = st.text_input("Enter XPath to Extract Text")

if st.button("Submit"):
    urls_list = urls.split('\n')
    results = []
    for url in urls_list:
        headers = {"User-Agent": user_agents}
        status_code = check_status_code(url) if check_status else "N/A"
        redirection = check_redirection(url) if check_redirection else "N/A"
        extracted_text = extract_text(url, xpath) if xpath else "N/A"
        results.append((url, status_code, redirection, extracted_text))
    
    # Display results in table
    st.table(results)
