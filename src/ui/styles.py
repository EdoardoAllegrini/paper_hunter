"""Streamlit UI styling for Paper Hunter."""


def get_page_config():
    """Get Streamlit page configuration with professional theme settings."""
    return {
        "page_title": "Paper Hunter",
        "page_icon": "📚",
        "layout": "wide",
        "initial_sidebar_state": "expanded",
    }


def get_custom_css():
    """Get professional CSS styling integrated seamlessly with Streamlit's native theming."""
    return """
    <style>
    hr {
        margin: none !important;
        padding: none !important;
    }
    div.stButton > button {
        padding: 2px 10px !important; /* Reduces internal spacing */
        height: 32px !important;      /* Forces a shorter button */
        min-height: 32px !important;  /* Overrides Streamlit's minimums */
        line-height: 1 !important;    /* Centers the '✕' vertically */
    }
    /* ===== METRIC STYLING ===== */
    /* Targets the large numeric value */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 700;
    }

    /* Targets the top label text */
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        opacity: 0.8;
    }
    /* ===== MODERN TABLE STYLING ===== */
    /* Using Streamlit's native CSS variables ensures perfect Light/Dark mode syncing */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
        font-family: var(--font-family);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        background-color: var(--background-color);
        color: var(--text-color);
        border: 1px solid var(--secondary-background-color);
    }

    .custom-table thead tr {
        /* Use Streamlit's native secondary background and text colors */
        background-color: var(--secondary-background-color);
        color: var(--text-color);

        /* Add a nice accent line underneath instead of filling the whole background */
        border-bottom: 2px solid var(--primary-color);

        text-align: left;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }

    .custom-table th {
        padding: 16px 15px;
        border: none;
    }

    .custom-table td {
        padding: 13px 15px;
        border-bottom: 1px solid var(--secondary-background-color);
    }

    .custom-table tbody tr {
        background-color: var(--background-color);
        transition: background-color 0.2s ease;
    }

    .custom-table tbody tr:nth-of-type(even) {
        background-color: var(--secondary-background-color);
    }

    .custom-table tbody tr:hover {
        /* Brightness filter works well dynamically in both light and dark modes */
        filter: brightness(0.95);
    }

    .custom-table a {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;
        transition: opacity 0.2s ease;
    }

    .custom-table a:hover {
        opacity: 0.8;
        text-decoration: underline;
    }

    /* ===== KEYWORD HIGHLIGHTING ===== */
    .highlight-pill {
        background-color: #fde047;
        color: #854d0e;
        border-radius: 4px;
        font-weight: 600;
        display: inline-block;
    }

    /* Target OS-level dark mode for specific contrast adjustments if needed */
    @media (prefers-color-scheme: dark) {
        .highlight-pill {
            background-color: #ca8a04;
            color: #fef08a;
        }
    }

    /* ===== RESPONSIVE DESIGN ===== */
    @media (max-width: 768px) {
        .custom-table {
            font-size: 13px;
        }
        .custom-table th, .custom-table td {
            padding: 10px 8px;
        }
    }
    </style>
    """
