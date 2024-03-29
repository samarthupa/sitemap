import streamlit as st
import requests
import csv
import pandas as pd
from io import BytesIO
from fake_useragent import UserAgent

# Function to check status code and redirection of URL
def check_status_and_redirection(url, user_agent):
    try:
        headers = {"User-Agent": user_agent}
        response = requests.get(url, headers=headers, allow_redirects=False)
        status_code = response.status_code
        redirection_urls = []
        max_redirections = 7  # Maximum number of redirections to follow
        redirection_count = 0
        if status_code in [301, 307, 302]:
            while 'location' in response.headers:
                redirection_count += 1
                if redirection_count > max_redirections:
                    break
                redirection_urls.append(response.headers['location'])
                response = requests.get(response.headers['location'], headers=headers, allow_redirects=False)
        return status_code, redirection_urls[:max_redirections]  # Return up to 7 redirection URLs
    except Exception as e:
        return str(e), "N/A"

# Streamlit UI
st.set_page_config(layout="wide")

st.title("Check and Fix Redirections")

# Input fields
urls = st.text_area("Enter URL(s) (one URL per line)", height=150)
user_agents = st.selectbox("Choose User Agent", ["Chrome", "Firefox", "Safari"])

if st.button("Submit"):
    with st.spinner("Processing... It may take some time if there are many URLs or Chain redirections."):
        ua = UserAgent()
        selected_user_agent = ""
        if user_agents == "Chrome":
            selected_user_agent = ua.chrome
        elif user_agents == "Firefox":
            selected_user_agent = ua.firefox
        elif user_agents == "Safari":
            selected_user_agent = ua.safari

        urls_list = urls.split('\n')
        unique_urls = set()  # To store unique URLs
        results = []
        max_redirections = 0
        final_destinations = []
        
        # Progress bar
        progress_bar = st.progress(0)
        for i, url in enumerate(urls_list):
            if url.strip() == '':  # Skip processing if the row is blank
                continue
            
            # Check if the URL is already processed
            if url in unique_urls:
                continue
            unique_urls.add(url)
            
            progress_percent = (i + 1) / len(urls_list)
            progress_bar.progress(progress_percent)
            
            status_code, redirection_urls = check_status_and_redirection(url, selected_user_agent)
            max_redirections = max(max_redirections, len(redirection_urls))
            results.append((url, status_code, *redirection_urls))
            final_destination = redirection_urls[-1] if redirection_urls else url
            final_destinations.append((url, status_code, final_destination))
        
        # Prepare column headers for main sheet
        main_headers = ['URL', 'Status Code']
        for i in range(max_redirections):
            main_headers.append(f'Redirection URL {i+1}')

        # Prepare data for main sheet
        main_data = [main_headers] + results

        # Prepare data for fix redirection sheet
        fix_redirection_headers = ['Original URL', 'Final Destination URL']
        fix_redirection_data = [fix_redirection_headers]

        for url, status_code, *redirection_urls in results:
            if status_code in [301, 302, 307]:
                original_urls = [url] + [redirect_url for redirect_url in redirection_urls if redirect_url]
                final_destination = redirection_urls[-1] if redirection_urls else url
                fix_redirection_data.extend([(original_url, final_destination) for original_url in original_urls if len(redirection_urls) > 1 and redirection_urls[1]])


        # Remove rows where Original URL and Final Destination URL are the same
        fix_redirection_data = [row for row in fix_redirection_data if row[0] != row[1]]

        # Create Excel file with two sheets
        excel_data = {'Redirections': main_data, 'Fix Redirections': fix_redirection_data}
        excel_file = BytesIO()
        excel_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        for sheet_name, sheet_data in excel_data.items():
            df = pd.DataFrame(sheet_data)
            df.to_excel(excel_writer, index=False, sheet_name=sheet_name, header=False)
        excel_writer.close()  # Close the writer
        excel_file.seek(0)

        # Display results in table
        st.table(main_data)

        # Download button for Excel file
        st.download_button(
            label="Download and Fix Redirection",
            data=excel_file,
            file_name="check_and_fix_redirections.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
