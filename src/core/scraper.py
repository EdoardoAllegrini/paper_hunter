"""DBLP paper scraper module."""

import requests
import streamlit as st
from bs4 import BeautifulSoup

from .models import Paper

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


@st.cache_data(show_spinner=False)
def fetch_dblp_papers(url: str, venue_name: str) -> list[Paper]:
    """
    Scrapes academic papers directly from a DBLP conference page.

    Args:
        url: The DBLP conference page URL
        venue_name: Display name for the venue (e.g., "USENIX Security 2024")

    Returns:
        List of Paper objects extracted from the page
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        papers = []

        # DBLP's consistent schema.org HTML tagging
        entries = soup.find_all("li", class_="entry")

        for entry in entries:
            cite_data = entry.find("cite", class_="data")
            if not cite_data:
                continue

            # Extract Authors
            author_spans = cite_data.find_all("span", itemprop="author")
            authors_list = [author.get_text(strip=True) for author in author_spans]
            authors_str = ", ".join(authors_list)

            # Extract Title
            title_span = cite_data.find("span", class_="title")
            title_str = title_span.get_text(strip=True) if title_span else "Unknown Title"

            # Skip empty or "front matter" entries
            if not authors_str or title_str == "Unknown Title":
                continue

            # Extract the specific paper URL
            link_tag = entry.select_one("nav.publ div.head a")
            paper_url = link_tag["href"] if link_tag else url

            papers.append(Paper(title=title_str, authors=authors_str, venue=venue_name, url=paper_url))

        return papers

    except requests.exceptions.RequestException as e:
        st.error(f"Error scraping {venue_name} at {url}: {e}")
        return []
