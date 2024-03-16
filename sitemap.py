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
        if status_code in [301, 307, 302]:
            while 'location' in response.headers:
                redirection_urls.append(response.headers['location'])
                response = requests.get(response.headers['location'], headers=headers, allow_redirects=False)
        return status_code, redirection_urls
    except Exception as e:
        return str(e), "N/A"

# Streamlit UI
st.set_page_config(layout="wide")

st.title("URL Analysis Tool")

# Input fields
urls = st.text_area("Enter URL(s) (one URL per line)", height=150)
user_agents = st.selectbox("Choose User Agent", ["Chrome", "Firefox", "Safari"])

if st.button("Submit"):
    with st.spinner("Processing..."):
        ua = UserAgent()
        selected_user_agent = ""
        if user_agents == "Chrome":
            selected_user_agent = ua.chrome
        elif user_agents == "Firefox":
            selected_user_agent = ua.firefox
        elif user_agents == "Safari":
            selected_user_agent = ua.safari

        urls_list = urls.split('\n')
        results = []
        max_redirections = 0
        final_destinations = []
        for url in urls_list:
            status_code, redirection_urls = check_status_and_redirection(url, selected_user_agent)
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
        excel_file = BytesIO()
        excel_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        for sheet_name, sheet_data in excel_data.items():
            df = pd.DataFrame(sheet_data)
            df.to_excel(excel_writer, index=False, sheet_name=sheet_name, header=False)
        excel_writer.close()  # Close the writer
        excel_file.seek(0)

        # Display results in table
        table = st.table(main_data)

        # Fullscreen button
        full_screen_col, table_col, _ = st.columns([0.1, 8, 0.1])
        full_screen_button = full_screen_col.empty()
        full_screen_button.button("🔍 Full Screen", key="full_screen")

        # Download button for Excel file
        st.download_button(
            label="Download Excel",
            data=excel_file,
            file_name="url_analysis_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Check if Full Screen button is clicked
        if full_screen_button.button_clicked("full_screen"):
            table.full_screen()
            # Minimize screen icon
            if st.button("🔍 Minimize Screen", key="minimize_screen"):
                table.window()
