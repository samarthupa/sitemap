import streamlit as st
import requests

# Proxy servers for different countries
proxies = {
    'USA': 'http://us-proxy.org',
    'UK': 'http://uk-proxy.org',
    'Germany': 'http://de-proxy.org',
    'Australia': 'http://au-proxy.org',
    'Brazil': 'http://br-proxy.org',
    'Japan': 'http://jp-proxy.org',
    'South Africa': 'http://za-proxy.org',
    'India': 'http://in-proxy.org',
    'China': 'http://cn-proxy.org',
}

# Function to check status code and redirection of URL
def check_status_and_redirection(url, country=None):
    try:
        if country:
            proxy = proxies.get(country)
            response = requests.get(url, proxies={'http': proxy, 'https': proxy}, allow_redirects=False)
        else:
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
country = st.selectbox("Choose Country", ["None", "USA", "UK", "Germany", "Australia", "Brazil", "Japan", "South Africa", "India", "China"])

if st.button("Submit"):
    urls_list = urls.split('\n')
    results = []
    for url in urls_list:
        status_code, redirection_urls = check_status_and_redirection(url, country)
        if redirection_urls:
            redirection_urls_str = ' -> '.join(redirection_urls)
        else:
            redirection_urls_str = "N/A"
        results.append((url, status_code, redirection_urls_str))
    
    # Display results in table
    st.table(results)
