"""Main Streamlit application for Paper Hunter."""

import pandas as pd
import streamlit as st

from src.core import VenueManager, fetch_dblp_papers, search_papers
from src.ui.components import highlight_keywords_html, render_html_table
from src.ui.styles import get_custom_css, get_page_config

# --- Initialize ---
st.set_page_config(**get_page_config())
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Session state
if "search_queue" not in st.session_state:
    st.session_state.search_queue = []

# Venue manager
venue_manager = VenueManager()


# --- Sidebar Controls ---
with st.sidebar:
    st.header("📌 1. Build Search Queue")

    venues = venue_manager.get_all()

    if not venues:
        st.warning("No venues found. Please add a venue below first.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_base = st.selectbox("Select Venue", options=list(venues.keys()))
        with col2:
            target_year = st.text_input("Year", value="2024")

        if st.button("Add to Queue", icon=":material/add:", use_container_width=True):
            if selected_base and target_year:
                target = {"name": selected_base, "acronym": venues[selected_base], "year": target_year.strip()}
                if target not in st.session_state.search_queue:
                    st.session_state.search_queue.append(target)
                    st.success(f"Added {selected_base} {target_year}")
                else:
                    st.info("Already in queue.")

    if st.session_state.search_queue:
        st.markdown("### Current Targets")

        # Display each venue with individual remove button
        for i, target in enumerate(st.session_state.search_queue):
            # 1. Adjust column ratio so the button column is compact
            col1, col2 = st.columns([6, 1])

            with col1:
                # 2. Add top margin to the text so it vertically centers with the button
                st.markdown(
                    f"<div style='margin-top: 0.45rem;'><b>{target['name']}</b> ({target['year']})</div>",
                    unsafe_allow_html=True,
                )

            with col2:
                # 3. Remove `use_container_width=True` to keep the button small and square
                if st.button("", icon=":material/delete:", key=f"remove_{i}", help="Remove venue", type="tertiary"):
                    st.session_state.search_queue.pop(i)
                    st.rerun()

        # Clear all button
        st.divider()
        if st.button(
            "Clear All", icon=":material/delete:", use_container_width=True, help="Remove all venues from queue"
        ):
            st.session_state.search_queue = []
            st.rerun()

    st.divider()

    st.header("🎯 2. Search Parameters")
    keywords_input = st.text_input("Keywords (comma separated):", placeholder="fuzzing, LLM, trusted execution")
    operator = st.radio("Logic Operator:", ["AND", "OR"], horizontal=True)

    search_button = st.button(
        icon=":material/search:", label="Execute Search", type="primary", use_container_width=True
    )

    st.divider()

    # Venue management
    with st.expander(icon=":material/settings:", label="Manage Venue Database"):
        st.markdown("##### Add New Venue")
        new_name = st.text_input("Venue Name", placeholder="e.g., USENIX Security")
        new_acronym = st.text_input("DBLP Acronym", placeholder="e.g., uss")

        if st.button("Save Venue"):
            if new_name and new_acronym:
                venue_manager.add(new_name, new_acronym)
                st.success(f"Added {new_name.strip()}!")
                st.rerun()
            else:
                st.error("Please provide both name and acronym.")

        st.markdown("---")
        st.markdown("##### Delete Venue")
        if venues:
            venue_to_delete = st.selectbox("Select to remove:", options=list(venues.keys()), key="del_box")
            if st.button("Delete Venue"):
                if venue_manager.delete(venue_to_delete):
                    # Remove from search queue too
                    st.session_state.search_queue = [
                        t for t in st.session_state.search_queue if t["name"] != venue_to_delete
                    ]
                    st.success(f"Deleted {venue_to_delete}!")
                    st.rerun()


# --- Main Content ---
st.markdown(
    """
    <style>
    .title-section {
        /* Use Streamlit's native secondary background for subtle borders */
        border-bottom: 2px solid var(--secondary-background-color);
    }
    .title-text {
        /* Links to Streamlit's active primary color */
        color: var(--primary-color);
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
    }
    .subtitle-text {
        /* Uses standard text color with opacity to look like a subtitle in any theme */
        color: var(--text-color);
        opacity: 0.7;
        font-size: 1rem;
        font-weight: 400;
        margin-top: 0.5rem;
    }
    </style>
    <div class="title-section">
        <div class="title-text">📚 Paper Hunter</div>
        <div class="subtitle-text">Queue venues, apply keyword filters, and discover research papers all in seconds!</div>
    </div>
    """,
    unsafe_allow_html=True,
)


if search_button:
    if not st.session_state.search_queue:
        st.warning("⚠️ Your search queue is empty. Please add at least one venue and year from the sidebar.")
    else:
        with st.spinner("⏳ Scraping venues... This might take a moment."):
            all_papers = []

            for target in st.session_state.search_queue:
                acr = target["acronym"]
                yr = target["year"]
                name = target["name"]

                url = f"https://dblp.org/db/conf/{acr}/{acr}{yr}.html"
                display_name = f"{name} {yr}"

                papers = fetch_dblp_papers(url=url, venue_name=display_name)
                all_papers.extend(papers)

            # Convert Paper objects to dicts for searching
            papers_dicts = [p.to_dict() for p in all_papers]
            matched = search_papers(all_papers, keywords_input, operator)
            matched_dicts = [p.to_dict() for p in matched]

        # Display Results
        if matched_dicts:
            st.markdown("---")
            st.markdown("### Search Results")

            df = pd.DataFrame(matched_dicts)
            # Metrics in columns
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Papers", len(all_papers))
            with col2:
                st.metric("Matched", len(matched_dicts))
            with col3:
                match_rate = (len(matched_dicts) / len(all_papers) * 100) if all_papers else 0
                st.metric("Match Rate", f"{match_rate:.1f}%")
            with col4:
                st.metric("Search Logic", operator)
            with col5:
                # Export button
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    icon=":material/file_download:",
                    label="Download Results",
                    data=csv,
                    file_name="dblp_papers_export.csv",
                    mime="text/csv",
                    use_container_width=False,
                    type="tertiary",
                )
            raw_keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

            st.markdown("")  # Spacing

            # Apply highlighting and render
            df["Title"] = df["Title"].apply(lambda x: highlight_keywords_html(x, raw_keywords))
            df["Authors"] = df["Authors"].apply(lambda x: highlight_keywords_html(x, raw_keywords))

            st.markdown(render_html_table(df), unsafe_allow_html=True)

        elif all_papers:
            st.markdown("---")
            st.info(
                f"📊 **{len(all_papers)} papers found** but none matched your keywords. "
                "Try broader terms or switch to 'OR' logic."
            )
        else:
            st.markdown("---")
            st.error(
                "❌ **No papers could be extracted.** Verify the DBLP acronyms and year are correct, "
                "or check your internet connection."
            )
