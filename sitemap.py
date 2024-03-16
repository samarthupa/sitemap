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
    fixed_redirections = []
    max_redirections = 0
    for url in urls_list:
        headers = {"User-Agent": user_agents}
        status_code, redirection_urls = check_status_and_redirection(url)
        max_redirections = max(max_redirections, len(redirection_urls))
        results.append((url, status_code, *redirection_urls))
        # If there are redirections, fix the redirection by getting the final destination URL
        if redirection_urls:
            fixed_redirections.append((url, redirection_urls[-1]))  # Append original URL and final destination URL
    
    # Prepare column headers for the results table
    headers_results = ['URL', 'Status Code']
    for i in range(max_redirections):
        headers_results.append(f'Redirection URL {i+1}')

    # Display results in table
    st.table([headers_results] + results)

    # Download button for CSV of original URLs and their fixed destinations
    if fixed_redirections:
        csv_data_fixed = StringIO()
        csv_writer_fixed = csv.writer(csv_data_fixed)
        csv_writer_fixed.writerow(['Original URL', 'Fixed Destination URL'])
        csv_writer_fixed.writerows(fixed_redirections)
        csv_text_fixed = csv_data_fixed.getvalue()
        st.download_button(
            label="Download Fixed Redirections CSV",
            data=csv_text_fixed,
            file_name="fixed_redirections.csv",
            mime="text/csv"
        )
