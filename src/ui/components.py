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
        """Generates highly distinct, consistent pastel colors from a string."""
        if not text or pd.isna(text):
            return "#f1f5f9", "#475569"  # Default slate gray for missing data

        # 1. Create a consistent integer hash from the venue name
        hash_int = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)

        # 2. Discretize the hue to force distinct colors
        # 12 buckets ensures colors are at least 30 degrees apart on the color wheel
        num_hue_buckets = 12
        hue = (hash_int % num_hue_buckets) * (360 // num_hue_buckets)

        # 3. Add minor variations to saturation to separate collisions
        # (between 70% and 95% saturation)
        sat = 70 + (hash_int % 26)

        # 4. Use HSL to guarantee readability
        # Background: soft pastel (lightness between 85% and 92%)
        bg_lightness = 85 + (hash_int % 8)
        # Text: dark high-contrast (lightness between 20% and 30%)
        text_lightness = 20 + (hash_int % 11)

        bg_color = f"hsl({hue}, {sat}%, {bg_lightness}%)"
        text_color = f"hsl({hue}, {sat}%, {text_lightness}%)"

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
