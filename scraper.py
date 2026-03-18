import requests
from bs4 import BeautifulSoup
import streamlit as st

@st.cache_data(show_spinner=False)
def fetch_dblp_papers(url, venue_name):
    """
    Scrapes academic papers directly from a DBLP conference page.
    Relies on DBLP's consistent schema.org HTML tagging.
    """
    try:
        # Headers help prevent requests from being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        papers = []
        
        # CHANGED: We now iterate over the parent <li> tags so we can access both the text data and the navigation links
        entries = soup.find_all('li', class_='entry')
        
        for entry in entries:
            # Find the cite tag which contains the text data
            cite_data = entry.find('cite', class_='data')
            if not cite_data:
                continue

            # 1. Extract Authors
            author_spans = cite_data.find_all('span', itemprop='author')
            authors_list = [author.get_text(strip=True) for author in author_spans]
            authors_str = ", ".join(authors_list)
            
            # 2. Extract Title
            title_span = cite_data.find('span', class_='title')
            title_str = title_span.get_text(strip=True) if title_span else "Unknown Title"
            
            # Skip empty or "front matter" entries (like conference preface)
            if not authors_str or title_str == "Unknown Title":
                continue
            
            # 3. Extract the specific paper URL (NEW)
            link_tag = entry.select_one('nav.publ div.head a')
            # If a specific link is found, use it; otherwise fallback to the general conference url
            paper_url = link_tag['href'] if link_tag else url 
                
            papers.append({
                "Venue": venue_name,
                "Title": title_str,
                "Authors": authors_str,
                "URL": paper_url  # Changed from the base 'url' variable
            })
            
        return papers

    except Exception as e:
        st.error(f"Error scraping {venue_name} at {url}: {e}")
        return []