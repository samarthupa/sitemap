import streamlit as st
import requests
import csv
from io import StringIO
import pandas as pd

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

# Function to get final destination URL
def get_final_destination(url):
    response = requests.get(url)
    return response.url

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

    # Create DataFrame for current data
    df_current = pd.DataFrame([headers] + results[1:], columns=headers)

    # Create DataFrame for fixed redirections
    fixed_redirections = []
    for url, _, *redirection_urls in results[1:]:
        final_destination = get_final_destination(url)
        fixed_redirections.append((url, final_destination))
    df_fixed_redirections = pd.DataFrame(fixed_redirections, columns=['URL', 'Final Destination'])

    # Download button for Excel with two tabs
    with st.spinner('Downloading...'):
        excel_writer = pd.ExcelWriter('url_analysis_results.xlsx', engine='xlsxwriter')
        df_current.to_excel(excel_writer, sheet_name='Current Data', index=False)
        df_fixed_redirections.to_excel(excel_writer, sheet_name='Fixed Redirections', index=False)
        excel_writer.save()
        st.success('Download Complete!')

    # Display results in table
    st.table(df_current)

    # Display fixed redirections
    st.subheader("Fixed Redirections")
    st.table(df_fixed_redirections)
