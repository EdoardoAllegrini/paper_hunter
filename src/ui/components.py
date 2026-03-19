import hashlib
import re
from typing import List

import pandas as pd


def render_html_table(df: pd.DataFrame) -> str:
    """
    Render a pandas DataFrame as a styled HTML table with dynamic,
    hash-based venue colors.

    Args:
        df: DataFrame with columns: Venue, Title, Authors, URL

    Returns:
        HTML string of the styled table
    """

    def get_deterministic_colors(text: str):
        """Generates a consistent pastel background and dark text color from a string."""
        if not text or pd.isna(text):
            return "#f1f5f9", "#475569"  # Default slate gray for missing data

        # 1. Create a consistent integer hash from the venue name
        hash_int = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)

        # 2. Map the hash to a hue degree (0 to 360)
        hue = hash_int % 360

        # 3. Use HSL to guarantee readability:
        # Background: 85% saturation, 92% lightness (soft pastel)
        # Text: 85% saturation, 25% lightness (dark, high contrast)
        bg_color = f"hsl({hue}, 85%, 92%)"
        text_color = f"hsl({hue}, 85%, 25%)"

        return bg_color, text_color

    html = "<table class='custom-table'>"
    html += "<thead><tr>"
    html += "<th>Venue</th>"
    html += "<th>Title</th>"
    html += "<th>Authors</th>"
    html += "<th style='text-align: center;'>Link</th>"
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        title = row.get("Title", "N/A")
        authors = row.get("Authors", "N/A")
        venue = str(row.get("Venue", "N/A"))
        url = row.get("URL", "#")

        # Get our dynamically generated, consistent colors
        bg_color, text_color = get_deterministic_colors(venue)

        html += "<tr>"
        html += f"<td><span style='background-color:{bg_color}; color:{text_color}; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.9em; white-space: nowrap;'>{venue}</span></td>"
        html += f"<td>{title}</td>"
        html += f"<td><i>{authors}</i></td>"
        html += f"<td style='text-align: center;'><a href='{url}' target='_blank' style='text-decoration: none; font-size: 1.2em;'>📄</a></td>"
        html += "</tr>"

    html += "</tbody></table>"
    return html


def highlight_keywords_html(text: str, keywords: List[str]) -> str:
    """
    Highlight keywords in text with HTML styling.

    Args:
        text: Text to highlight
        keywords: List of keywords to highlight

    Returns:
        HTML string with highlighted keywords
    """
    if not text or pd.isna(text) or not keywords:
        return str(text) if text else ""

    text = str(text)
    sorted_kws = sorted(keywords, key=len, reverse=True)

    for kw in sorted_kws:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        text = pattern.sub(lambda m: f"<span class='highlight-pill'>{m.group(0)}</span>", text)

    return text
