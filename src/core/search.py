"""Search functionality for papers."""

from typing import List

from .models import Paper


def search_papers(papers: List[Paper], keywords_str: str, operator: str) -> List[Paper]:
    """
    Filter papers based on keywords and logical operator.

    Args:
        papers: List of papers to search
        keywords_str: Comma-separated keywords
        operator: "AND" or "OR" logical operator

    Returns:
        Filtered list of papers
    """
    if not keywords_str.strip():
        return papers

    keywords = [k.strip().lower() for k in keywords_str.split(",") if k.strip()]
    results = []

    for paper in papers:
        text_to_search = f"{paper.title} {paper.authors}".lower()

        if operator == "AND" and all(kw in text_to_search for kw in keywords):
            results.append(paper)
        elif operator == "OR" and any(kw in text_to_search for kw in keywords):
            results.append(paper)

    return results
