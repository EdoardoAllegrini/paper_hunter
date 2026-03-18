import streamlit as st
import pandas as pd
import json
import os
from scraper import fetch_dblp_papers

# --- Configuration ---
st.set_page_config(page_title="DBLP Paper Finder", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="st-"], [class*="css"], p, div, span, label {
        font-size: 16px !important; 
    }
    [data-testid="stSidebar"] * {
        font-size: 16px !important;
    }
    [data-testid="stHeadingWithActionElements"] h1, h1 {
        font-size: 30px !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- Venue Management Functions ---
VENUES_FILE = "venues.json"

def load_venues():
    if os.path.exists(VENUES_FILE):
        with open(VENUES_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_venues(venues_dict):
    with open(VENUES_FILE, "w") as f:
        json.dump(venues_dict, f, indent=4)

def search_papers(papers, keywords_str, operator):
    if not keywords_str.strip():
        return papers
        
    keywords = [k.strip().lower() for k in keywords_str.split(',') if k.strip()]
    results = []
    
    for paper in papers:
        text_to_search = f"{paper.get('Title', '')} {paper.get('Authors', '')}".lower()
        if operator == "AND" and all(kw in text_to_search for kw in keywords):
            results.append(paper)
        elif operator == "OR" and any(kw in text_to_search for kw in keywords):
            results.append(paper)
    return results

# Load existing venues into memory
VENUES = load_venues()

# --- UI Layout ---
st.title("📚 DBLP Security & Privacy Paper Finder")

# Sidebar Controls
with st.sidebar:
    st.header("Search Parameters")
    
    selected_venues = st.multiselect(
        "Select Venues:",
        options=list(VENUES.keys())
    )
    
    # New global year input for the search
    target_year = st.text_input("Target Year:", value="2024", placeholder="e.g., 2024")
    
    keywords_input = st.text_input("Keywords (comma separated):", placeholder="fuzzing, LLM")
    operator = st.radio("Search Logic:", ["AND", "OR"])
    
    st.divider()
    search_button = st.button("🔍 Execute Search", type="primary", use_container_width=True)
    
    st.divider()
    
    # --- Add New Venue UI ---
    with st.expander("➕ Add New Venue"):
        new_name = st.text_input("Venue Name", placeholder="e.g., USENIX Security")
        new_acronym = st.text_input("DBLP Acronym", placeholder="e.g., uss")
        # Year input removed from here!
        
        if st.button("Save Venue", use_container_width=True):
            if new_name and new_acronym:
                name_clean = new_name.strip()
                acr_clean = new_acronym.strip().lower()
                
                # Store just the name and acronym mapping
                VENUES[name_clean] = acr_clean
                save_venues(VENUES)
                
                st.success(f"Added {name_clean}!")
                st.rerun() 
            else:
                st.error("Please provide both name and acronym.")
                
    # --- Delete Venue UI ---
    with st.expander("🗑️ Delete Saved Venue"):
        if not VENUES:
            st.info("No venues saved yet.")
        else:
            venue_to_delete = st.selectbox(
                "Select venue to remove:", 
                options=list(VENUES.keys())
            )
            
            if st.button("Delete Venue", use_container_width=True):
                if venue_to_delete in VENUES:
                    del VENUES[venue_to_delete]
                    save_venues(VENUES)
                    st.success(f"Deleted {venue_to_delete}!")
                    st.rerun() 

# Main Logic execution
if search_button:
    if not selected_venues:
        st.warning("Please select at least one venue.")
    elif not target_year.strip():
        st.warning("Please specify a target year.")
    else:
        with st.spinner('Fetching papers directly from DBLP...'):
            all_papers = []
            yr = target_year.strip()
            
            for venue in selected_venues:
                acr = VENUES[venue]
                # Dynamically construct the URL here
                url = f"https://dblp.org/db/conf/{acr}/{acr}{yr}.html"
                
                # Fetch papers 
                papers = fetch_dblp_papers(url=url, venue_name=f"{venue} {yr}")
                if papers:
                    all_papers.extend(papers)
            
            # Apply keyword search logic
            matched_papers = search_papers(all_papers, keywords_input, operator)
            
        # Display Results
        if matched_papers:
            st.success(f"Successfully extracted and found {len(matched_papers)} matching papers!")
            
            df = pd.DataFrame(matched_papers)
            st.dataframe(
                df, 
                column_config={"URL": st.column_config.LinkColumn("Source Link")},
                hide_index=True,
                use_container_width=True
            )
        elif all_papers:
            st.info("Papers were extracted, but none matched your keywords.")