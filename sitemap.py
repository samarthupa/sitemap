import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to check status code and handle redirection
def check_status_and_redirection(url):
    try:
        response = requests.get(url)
        status_code = response.status_code
        if status_code == 200:
            redirection = "No Redirection"
        elif status_code in [301, 302, 307]:
            redirection = response.headers['Location']
        else:
            redirection = "N/A"
        return status_code, redirection
    except:
        return "N/A", "N/A"

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
check_extraction = st.checkbox("Extract Text using XPath")
xpath = st.text_input("Enter XPath to Extract Text")

if st.button("Submit"):
    urls_list = urls.split('\n')
    results = []
    for url in urls_list:
        headers = {"User-Agent": user_agents}
        status, redirection = check_status_and_redirection(url) if check_redirection else ("N/A", "N/A")
        extracted_text = extract_text(url, xpath) if check_extraction else "N/A"
        results.append((url, status if check_status else "N/A", redirection if check_redirection else "N/A", extracted_text if check_extraction else "N/A"))
    
    # Display results in table
    st.table(results)
