import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse


# Function to extract URLs from a sitemap
def extract_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url, timeout=10)  # Set timeout value (in seconds)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = soup.find_all('loc')
        return [url.text for url in urls]
    except requests.exceptions.RequestException as e:
        st.error(f"Error occurred: {str(e)}")



# Function to parse and extract domain from URL
def get_domain(url):
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain

# Main function
def main():
    st.title("Sitemap URL Extractor")

    # Input for entering sitemap URLs
    st.subheader("Enter Sitemap URLs (One URL per line)")
    sitemaps_input = st.text_area("Paste Sitemap URLs here", height=200)

    if st.button("Extract URLs"):
        sitemaps = sitemaps_input.split('\n')
        all_urls = []
        for sitemap in sitemaps:
            urls = extract_urls_from_sitemap(sitemap)
            all_urls.extend(urls)

        # Display extracted URLs
        st.subheader("Extracted URLs:")
        for url in all_urls:
            st.write(url)

        # Create DataFrame
        df = pd.DataFrame({'URL': all_urls})

        # Download as CSV
        st.subheader("Download as CSV")
        csv_download = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="Download CSV",
            data=csv_download,
            file_name="sitemap_urls.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
