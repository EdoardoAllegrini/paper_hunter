"""Core functionality for Paper Hunter."""

from .scraper import fetch_dblp_papers
from .search import search_papers
from .venue_manager import VenueManager

__all__ = ["fetch_dblp_papers", "VenueManager", "search_papers"]
