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
if "show_save_toast" not in st.session_state:
    st.session_state.show_save_toast = False

# Trigger the toast if the flag is True
if st.session_state.show_save_toast:
    st.toast("Queue successfully saved!", icon="✅")
    st.session_state.show_save_toast = False  # Reset it immediately

# Venue manager
venue_manager = VenueManager()


# --- Sidebar Controls ---
with st.sidebar:
    st.title("⚙️ Configuration")

    # ==========================================
    # 1. BUILD SEARCH QUEUE (Primary Action)
    # ==========================================
    st.header("1. Target Venues")

    venues = venue_manager.get_all()
    if not venues:
        st.warning("No venues found. Please add a venue in Utilities below.")
    else:
        # Add to Queue Form
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_base = st.selectbox("Select Venue", options=list(venues.keys()), label_visibility="collapsed")
        with col2:
            target_year = st.text_input("Year", value="2024", label_visibility="collapsed")

        if st.button("Add to Queue", icon=":material/add:", use_container_width=True):
            if selected_base and target_year:
                target = {"name": selected_base, "acronym": venues[selected_base], "year": target_year.strip()}
                if target not in st.session_state.search_queue:
                    st.session_state.search_queue.append(target)
                    st.toast(f"Added {selected_base} '{target_year[-2:]} to queue!", icon="✅")
                else:
                    st.toast("Already in queue.", icon="ℹ️")

    # Active Queue Display
    if st.session_state.search_queue:
        st.markdown(
            "<p style='font-size: 0.9rem; margin-bottom: 0.2rem; margin-top: 1rem;'><b>Current Queue</b></p>",
            unsafe_allow_html=True,
        )

        # Enclose queue in a visual box for better grouping
        with st.container(border=True):
            for i, target in enumerate(st.session_state.search_queue):
                col_name, col_btn = st.columns([5, 1])
                with col_name:
                    st.markdown(
                        f"<div style='margin-top: 0.35rem; font-size: 0.9rem;'>{target['name']} ({target['year']})</div>",
                        unsafe_allow_html=True,
                    )
                with col_btn:
                    if st.button("", icon=":material/close:", key=f"remove_{i}", help="Remove", type="tertiary"):
                        st.session_state.search_queue.pop(i)
                        st.rerun()

            # Queue Actions (Clear & Save)
            col_clear, col_save = st.columns(2)
            with col_clear:
                if st.button(
                    "", icon=":material/delete:", use_container_width=True, type="tertiary", help="Clear queue"
                ):
                    st.session_state.search_queue = []
                    st.rerun()
            with col_save:
                # UX FIX: Use popover to hide the save input until requested
                with st.popover("", icon=":material/save:", use_container_width=True, type="tertiary"):
                    preset_name = st.text_input("Preset Name", placeholder="e.g., USENIX+S&P '24")
                    if st.button("Save", type="primary", use_container_width=True):
                        if preset_name:
                            venue_manager.save_preset(preset_name, st.session_state.search_queue)
                            st.session_state.show_save_toast = True
                            st.rerun()
                        else:
                            st.error("Name required.")

    st.divider()

    # ==========================================
    # 2. UTILITIES & ADMIN (Secondary Actions)
    # ==========================================
    st.markdown("### 🛠️ Utilities")

    # Manage Saved Queues (Presets)
    presets = venue_manager.get_presets()
    with st.expander(icon=":material/bookmarks:", label=f"Saved Queues ({len(presets) if presets else 0})"):
        if presets:
            selected_preset = st.selectbox(
                "Choose a saved queue", options=list(presets.keys()), label_visibility="collapsed"
            )
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("Load", icon=":material/download:", use_container_width=True):
                    st.session_state.search_queue = [dict(item) for item in presets[selected_preset]]
                    st.rerun()
            with col_p2:
                if st.button("Delete", type="tertiary", icon=":material/delete:", use_container_width=True):
                    venue_manager.delete_preset(selected_preset)
                    st.rerun()
        else:
            st.caption("No saved queues yet.")

    # Manage Venue Database
    with st.expander(icon=":material/database:", label=f"Venue Database ({len(venues) if venues else 0})"):
        st.markdown("**Add New Venue**")
        new_name = st.text_input("Venue Name", placeholder="e.g., USENIX Security", label_visibility="collapsed")
        new_acronym = st.text_input("DBLP Acronym", placeholder="e.g., uss", label_visibility="collapsed")

        if st.button("Save Venue", icon=":material/add_circle:", use_container_width=True):
            if new_name and new_acronym:
                venue_manager.add(new_name, new_acronym)
                st.success(f"Added {new_name.strip()}!")
                st.rerun()
            else:
                st.error("Please provide both.")

        if venues:
            st.divider()
            st.markdown("**Delete Venue**")
            venue_to_delete = st.selectbox(
                "Select to remove:", options=list(venues.keys()), key="del_box", label_visibility="collapsed"
            )
            if st.button("Delete Venue", icon=":material/delete:", type="tertiary", use_container_width=True):
                if venue_manager.delete(venue_to_delete):
                    st.session_state.search_queue = [
                        t for t in st.session_state.search_queue if t["name"] != venue_to_delete
                    ]
                    st.success(f"Deleted {venue_to_delete}!")
                    st.rerun()


# --- Main Content ---
# Create two columns for the header area: one for the title, one for the search box
header_col, search_col = st.columns([1.2, 1])

with header_col:
    st.markdown(
        """
        <style>
        .title-section {
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        .title-text {
            color: var(--primary-color);
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            padding: 0;
            line-height: 1.2;
        }
        .subtitle-text {
            color: var(--text-color);
            opacity: 0.8;
            font-size: 1.1rem;
            font-weight: 400;
            margin-top: 0.5rem;
        }
        </style>
        <div class="title-section">
            <div class="title-text">📚 Paper Hunter</div>
            <div class="subtitle-text">Queue venues, apply keyword filters, and discover research papers in seconds.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with search_col:
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)  # Vertical alignment buffer
    keywords_input = st.text_input(
        "Keywords",
        placeholder="e.g., fuzzing, LLM, trusted execution",
        help="Comma separated values",
        label_visibility="collapsed",
    )

    op_col, btn_col = st.columns([1, 1])
    with op_col:
        operator = st.radio("Logic Operator:", ["AND", "OR"], horizontal=True, label_visibility="collapsed")
    with btn_col:
        search_button = st.button(icon=":material/search:", label="SEARCH", type="primary", use_container_width=True)

st.divider()


# --- Execution Logic ---
if search_button:
    if not st.session_state.search_queue:
        st.warning("⚠️ Your search queue is empty. Please add at least one venue and year from the sidebar.")
    else:
        all_papers = []
        total_venues = len(st.session_state.search_queue)

        # 1. Create empty placeholders for our dynamic UI
        status_msg = st.empty()
        progress_bar = st.progress(0)

        # 2. Iterate through the queue and update the UI
        for i, target in enumerate(st.session_state.search_queue):
            acr = target["acronym"]
            yr = target["year"]
            name = target["name"]
            display_name = f"{name} {yr}"

            # Update the message with the specific conference being fetched
            status_msg.info(f"🏃‍♂️ **Fetching papers...** Currently grabbing {display_name} ({i + 1} of {total_venues})")

            url = f"https://dblp.org/db/conf/{acr}/{acr}{yr}.html"
            papers = fetch_dblp_papers(url=url, venue_name=display_name)
            all_papers.extend(papers)

            # Update the progress bar mathematically
            progress_bar.progress((i + 1) / total_venues)

        # 3. Clean up the loading UI once the heavy lifting is done
        status_msg.empty()
        progress_bar.empty()

        # 4. Use a quick, standard spinner for the local text-matching phase
        with st.spinner("🔍 Filtering your keywords..."):
            matched = search_papers(all_papers, keywords_input, operator)
            matched_dicts = [p.to_dict() for p in matched]

        # Display Results
        if matched_dicts:
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
                    label="Export",
                    data=csv,
                    file_name="dblp_papers_export.csv",
                    mime="text/csv",
                    use_container_width=True,
                    type="tertiary",
                )
            raw_keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

            st.markdown("<br>", unsafe_allow_html=True)  # Spacing

            # Apply highlighting and render
            df["Title"] = df["Title"].apply(lambda x: highlight_keywords_html(x, raw_keywords))
            df["Authors"] = df["Authors"].apply(lambda x: highlight_keywords_html(x, raw_keywords))

            st.markdown(render_html_table(df), unsafe_allow_html=True)

        elif all_papers:
            st.info(
                f"📊 **{len(all_papers)} papers found** but none matched your keywords. "
                "Try broader terms or switch to 'OR' logic."
            )
        else:
            st.error(
                "❌ **No papers could be extracted.** Verify the DBLP acronyms and year are correct, "
                "or check your internet connection."
            )
