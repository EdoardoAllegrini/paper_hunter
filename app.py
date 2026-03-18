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

# --- State Management ---
# Initialize a session state to hold the specific venue+year targets for the current search
if "search_queue" not in st.session_state:
    st.session_state.search_queue = []

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

# Load base venues into memory
VENUES = load_venues()

# --- UI Layout ---
st.title("📚 DBLP Security & Privacy Paper Finder")

# Sidebar Controls
with st.sidebar:
    st.header("1. Build Search Queue")
    
    if not VENUES:
        st.warning("No venues found. Please add a venue below first.")
    else:
        # Inputs to build a specific search target
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_base = st.selectbox("Select Venue", options=list(VENUES.keys()))
        with col2:
            target_year = st.text_input("Year", value="2024")
            
        if st.button("➕ Add to Queue", width="stretch"):
            if selected_base and target_year:
                target = {
                    "name": selected_base,
                    "acronym": VENUES[selected_base],
                    "year": target_year.strip()
                }
                # Prevent duplicates in the queue
                if target not in st.session_state.search_queue:
                    st.session_state.search_queue.append(target)
                    st.success(f"Added {selected_base} {target_year}")
                else:
                    st.info("Already in queue.")

    # Display the current queue
    if st.session_state.search_queue:
        st.markdown("**Current Search Targets:**")
        for i, target in enumerate(st.session_state.search_queue):
            st.markdown(f"- {target['name']} {target['year']}")
            
        if st.button("🗑️ Clear Queue"):
            st.session_state.search_queue = []
            st.rerun()

    st.divider()

    st.header("2. Keywords & Execute")
    keywords_input = st.text_input("Keywords (comma separated):", placeholder="fuzzing, LLM")
    operator = st.radio("Search Logic:", ["AND", "OR"])
    
    search_button = st.button("🔍 Execute Search", type="primary", width="stretch")
    
    st.divider()
    
    # --- Manage Database Expanders ---
    with st.expander("⚙️ Manage Venue Database"):
        st.markdown("**Add New Venue**")
        new_name = st.text_input("Venue Name", placeholder="e.g., USENIX Security")
        new_acronym = st.text_input("DBLP Acronym", placeholder="e.g., uss")
        
        if st.button("Save to Database", width="stretch"):
            if new_name and new_acronym:
                VENUES[new_name.strip()] = new_acronym.strip().lower()
                save_venues(VENUES)
                st.success(f"Added {new_name.strip()}!")
                st.rerun() 
            else:
                st.error("Please provide both name and acronym.")
                
        st.markdown("---")
        st.markdown("**Delete Saved Venue**")
        if VENUES:
            venue_to_delete = st.selectbox("Select to remove:", options=list(VENUES.keys()), key="del_box")
            if st.button("Delete from Database", width="stretch"):
                if venue_to_delete in VENUES:
                    del VENUES[venue_to_delete]
                    save_venues(VENUES)
                    
                    # Also clean up the search queue if the deleted venue was in it
                    st.session_state.search_queue = [t for t in st.session_state.search_queue if t["name"] != venue_to_delete]
                    
                    st.success(f"Deleted {venue_to_delete}!")
                    st.rerun() 

# Main Logic execution
if search_button:
    if not st.session_state.search_queue:
        st.warning("Your search queue is empty. Please add at least one venue and year from the sidebar.")
    else:
        with st.spinner('Fetching papers directly from DBLP...'):
            all_papers = []
            
            # Loop through the specific targets the user built
            for target in st.session_state.search_queue:
                acr = target["acronym"]
                yr = target["year"]
                name = target["name"]
                
                # Construct URL
                url = f"https://dblp.org/db/conf/{acr}/{acr}{yr}.html"
                display_name = f"{name} {yr}"
                
                # Fetch papers 
                papers = fetch_dblp_papers(url=url, venue_name=display_name)
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
                column_config={"URL": st.column_config.LinkColumn("Paper Link")},
                hide_index=True,
                width="stretch"
            )
        elif all_papers:
            st.info("Papers were extracted, but none matched your keywords.")