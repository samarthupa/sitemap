import streamlit as st
import requests
import csv
from io import StringIO

# Function to check status code and redirection of URL
def check_status_and_redirection(url):
    try:
        response = requests.get(url, allow_redirects=False)
        status_code = response.status_code
        redirection_urls = []
        if status_code in [301, 307, 302]:
            while 'location' in response.headers:
                redirection_urls.append(response.headers['location'])
                response = requests.get(response.headers['location'], allow_redirects=False)
        return status_code, redirection_urls
    except Exception as e:
        return str(e), "N/A"

# Streamlit UI
st.title("URL Analysis Tool")

# Input fields
urls = st.text_area("Enter URL(s) (one URL per line)", height=150)
user_agents = st.selectbox("Choose User Agent", ["Chrome", "Firefox", "Safari"])

if st.button("Submit"):
    urls_list = urls.split('\n')
    results = []
    max_redirections = 0
    for url in urls_list:
        headers = {"User-Agent": user_agents}
        status_code, redirection_urls = check_status_and_redirection(url)
        max_redirections = max(max_redirections, len(redirection_urls))
        results.append((url, status_code, *redirection_urls))
    
    # Prepare column headers
    headers = ['URL', 'Status Code']
    for i in range(max_redirections):
        headers.append(f'Redirection URL {i+1}')

    # Display results in table without column numbering
    st.write("## Analysis Results")
    st.table(results)

    # Download button for CSV
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(headers)
    csv_writer.writerows(results)
    csv_text = csv_data.getvalue()
    st.download_button(
        label="Download CSV",
        data=csv_text,
        file_name="url_analysis_results.csv",
        mime="text/csv"
    )
