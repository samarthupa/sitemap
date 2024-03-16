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
st.title("URL Analysis Tool")

# Input fields
col1, col2 = st.columns([3, 1])
with col1:
    urls = st.text_area("Enter URL(s) (one URL per line)", height=150)
with col2:
    st.text("")  # Placeholder for layout alignment

st.write("")  # Empty space

# Zoom buttons
zoom_in, _, zoom_out = st.columns([1, 3, 1])
with zoom_in:
    if st.button("Zoom In"):
        st.markdown("<style> .css-1j9b1kc {transform: scale(1.1);}</style>", unsafe_allow_html=True)

with zoom_out:
    if st.button("Zoom Out"):
        st.markdown("<style> .css-1j9b1kc {transform: scale(0.9);}</style>", unsafe_allow_html=True)

st.write("")  # Empty space

# Submit button
submit_button = st.button("Submit")

# Process when submit button is clicked
if submit_button:
    with st.spinner("Analyzing URLs. Please wait..."):
        ua = UserAgent()
        selected_user_agent = ua.chrome  # Default user agent
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
        st.table(main_data)

        # Download button for Excel file
        st.download_button(
            label="Download Excel",
            data=excel_file,
            file_name="url_analysis_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
