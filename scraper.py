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
        
        # DBLP wraps paper metadata in <cite class="data"> tags
        entries = soup.find_all('cite', class_='data')
        
        for entry in entries:
            # 1. Extract Authors: DBLP uses <span itemprop="author">
            author_spans = entry.find_all('span', itemprop='author')
            authors_list = [author.get_text(strip=True) for author in author_spans]
            authors_str = ", ".join(authors_list)
            
            # 2. Extract Title: DBLP uses <span class="title">
            title_span = entry.find('span', class_='title')
            title_str = title_span.get_text(strip=True) if title_span else "Unknown Title"
            
            # Skip empty or "front matter" entries (like conference preface)
            if not authors_str or title_str == "Unknown Title":
                continue
                
            papers.append({
                "Venue": venue_name,
                "Title": title_str,
                "Authors": authors_str,
                "URL": url
            })
            
        return papers

    except Exception as e:
        st.error(f"Error scraping {venue_name} at {url}: {e}")
        return []