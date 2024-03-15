import streamlit as st
import requests
from lxml import html

# Function to fetch data based on user input
def fetch_data(url, user_agent, options, xpath):
    results = {}
    
    # Set user agent
    headers = {'User-Agent': user_agent}
    
    # Fetch page content
    response = requests.get(url, headers=headers)
    
    # Check status code
    if 'Check Status Code' in options:
        results['Status Code'] = response.status_code
    
    # Check redirection
    if 'Check Redirection' in options:
        results['Redirection'] = response.history
    
    # Check indexibility
    if 'Check Indexibility' in options:
        # Add indexibility check logic here
        results['Indexibility'] = 'To be implemented'
    
    # Extract text using XPath
    if 'Extract Text' in options and xpath:
        tree = html.fromstring(response.content)
        extracted_text = tree.xpath(xpath)
        results['Extracted Text'] = extracted_text
    
    return results

# Main function to run the Streamlit app
def main():
    st.title("URL Checker")
    
    # User input section
    st.header("Enter URLs")
    urls = st.text_area("Enter URLs (one per line)")
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    ]
    user_agent = st.selectbox("Choose User Agent", user_agents)
    
    options = st.multiselect("Select Options", ["Check Status Code", "Check Redirection", "Check Indexibility", "Extract Text"])
    
    xpath = ""
    if 'Extract Text' in options:
        xpath = st.text_input("Enter XPath to Extract Text")
    
    if st.button("Submit"):
        urls_list = urls.split("\n")
        results = []
        
        # Iterate over each URL and fetch data
        for url in urls_list:
            if url.strip() != "":
                data = fetch_data(url.strip(), user_agent, options, xpath)
                results.append(data)
        
        # Display results in a table
        st.header("Results")
        for i, result in enumerate(results):
            st.subheader(f"URL {i+1}")
            st.table(result)

if __name__ == "__main__":
    main()
