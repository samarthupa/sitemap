import streamlit as st
import requests
import csv
import pandas as pd
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
    final_destinations = []
    for url in urls_list:
        headers = {"User-Agent": user_agents}
        status_code, redirection_urls = check_status_and_redirection(url)
        max_redirections = max(max_redirections, len(redirection_urls))
        results.append((url, status_code, *redirection_urls))
        final_destination = redirection_urls[-1] if redirection_urls else url
        final_destinations.append((url, final_destination))
    
    # Prepare column headers for main sheet
    main_headers = ['URL', 'Status Code']
    for i in range(max_redirections):
        main_headers.append(f'Redirection URL {i+1}')

    # Prepare data for main sheet
    main_data = [main_headers] + results

    # Prepare data for fix redirection sheet
    fix_redirection_headers = ['Original URL', 'Final Destination URL']
    fix_redirection_data = [fix_redirection_headers] + final_destinations

    # Create Excel file with two sheets
    excel_data = {'Main Sheet': main_data, 'Fix Redirection': fix_redirection_data}
    excel_file = pd.ExcelWriter('url_analysis_results.xlsx', engine='xlsxwriter')
    for sheet_name, sheet_data in excel_data.items():
        df = pd.DataFrame(sheet_data)
        df.to_excel(excel_file, index=False, sheet_name=sheet_name, header=False)
    excel_file.save()

    # Display results in table
    st.table(main_data)

    # Download button for Excel file
    st.download_button(
        label="Download Excel",
        data=open('url_analysis_results.xlsx', 'rb'),
        file_name="url_analysis_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
