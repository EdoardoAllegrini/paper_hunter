import time

import requests
import streamlit as st
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import Paper

# 1. USE A POLITE USER-AGENT
HEADERS = {
    "User-Agent": "AcademicScraperBot/1.0 (mailto:edosemail@gmail.com)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _create_session_with_retries():
    """Create a requests session with retry logic for handling 503 errors."""
    session = requests.Session()

    # Increased backoff factor slightly to be safer
    retry_strategy = Retry(
        total=3,
        backoff_factor=3,  # Wait 3, 6, 12 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


# 2. GLOBALIZE THE SESSION
# Reusing the same session maintains connection pools and reduces overhead
SCRAPER_SESSION = _create_session_with_retries()


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
        # Keep the delay to respect rate limits (DBLP asks for 1 req/sec max)
        time.sleep(1.5)

        # Use the global session
        response = SCRAPER_SESSION.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        papers = []

        entries = soup.find_all("li", class_="entry")

        for entry in entries:
            cite_data = entry.find("cite", class_="data")
            if not cite_data:
                continue

            author_spans = cite_data.find_all("span", itemprop="author")
            authors_list = [author.get_text(strip=True) for author in author_spans]
            authors_str = ", ".join(authors_list)

            title_span = cite_data.find("span", class_="title")
            title_str = title_span.get_text(strip=True) if title_span else "Unknown Title"

            if not authors_str or title_str == "Unknown Title":
                continue

            link_tag = entry.select_one("nav.publ div.head a")
            paper_url = link_tag["href"] if link_tag else url

            papers.append(Paper(title=title_str, authors=authors_str, venue=venue_name, url=paper_url))

        return papers

    except requests.exceptions.RequestException as e:
        st.error(f"Network error scraping {venue_name}: {e}")
        return []
    except Exception as e:
        st.error(f"Parsing error on {venue_name}: {e}")
        return []
