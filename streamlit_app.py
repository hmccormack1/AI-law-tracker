import pandas as pd
import requests
import streamlit as st

from law_tracker import get_laws, LAW_AI_TRACKER_API_KEY
from config import PAGE_SIZE


# ----------------------------------------------------------------
# Intro - tell the user what this app does before asking for anything
# ----------------------------------------------------------------

st.title("🤖⚖️ AI Law Tracker")

st.write(
    """
    This app looks up real, tracked AI-related laws using the
    [AI Law Tracker API](https://ai-law-tracker.com). Choose one or more
    states (or US-Federal), what stage of the lawmaking process you care
    about, and any keyword you're curious about, then hit **Go**.
    """
)


# Set session variables for pagination
if "page" not in st.session_state:
    st.session_state.page = 0

if "search" not in st.session_state:
    st.session_state.search = None


# ----------------------------------------------------------------
# Load the list of US jurisdictions (all 50 states + US-Federal) once per
# session, so the dropdown below has real options instead of free text.
# @st.cache_data means this only actually calls the API the first time -
# later reruns reuse the cached result instead of hitting the API again.
# ----------------------------------------------------------------

@st.cache_data
def load_us_jurisdictions():
    url = "https://ai-law-tracker.com/api/v1/jurisdictions"
    headers = {"X-API-Key": LAW_AI_TRACKER_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    all_jurisdictions = response.json()["data"]

    # Keep only individual US states and the US-Federal entry - this is what
    # limits the whole app to US law instead of also offering EU/global options.
    return [j for j in all_jurisdictions if j["scope"] in ("state", "federal")]


us_jurisdictions = load_us_jurisdictions()

# Build a lookup from the friendly name shown to the user ("Colorado") back
# to the slug the API actually expects ("colorado").
name_to_slug = {j["name"]: j["slug"] for j in us_jurisdictions}
jurisdiction_names = sorted(name_to_slug.keys())

# ----------------------------------------------------------------
# Ask the user for the filters, in plain language
# ----------------------------------------------------------------

selected_names = st.multiselect(
    "Which state(s) would you like to look up AI laws for? "
    "(Choose United States (Federal) for federal law.)",
    options=jurisdiction_names,
)

status = st.text_input(
    "What status are you interested in?",
    placeholder="e.g. Signed, Introduced, Effective",
)

keyword = st.text_input(
    "Any keyword you'd like to search for?",
    placeholder="e.g. facial recognition, healthcare",
)

# We use a button instead of running the search on every keystroke.
# Streamlit reruns the whole script whenever a widget changes, so without
# a button, we'd call the API after every letter typed into any box.
go = st.button("Go")

# ----------------------------------------------------------------
# On "Go", call the API and show the results as a table
# ----------------------------------------------------------------

# When go but is hit, return to first page
if go:
    if not selected_names:
        st.warning("Please select at least one state or US-Federal first.")
    else:
        selected_slugs = [name_to_slug[name] for name in selected_names]

        st.session_state.search = {
            "jurisdiction": selected_slugs,
            "status": status.strip(),
            "keyword": keyword.strip(),
        }

        st.session_state.page = 0


# Show results whenever a search has been submitted.
# This remains true when Previous / Next cause Streamlit to rerun.
if st.session_state.search is not None:
    search = st.session_state.search
    offset = st.session_state.page * PAGE_SIZE

    result = get_laws(
        jurisdiction=search["jurisdiction"],
        status=search["status"],
        keyword=search["keyword"],
        limit=PAGE_SIZE,
        offset=offset,
    )

    if result is None:
        st.error(
            "Something went wrong calling the API. "
            "Check your API key or inputs and try again."
        )

    else:
        laws = result["data"]
        meta = result["meta"]

        total = meta["total"]
        limit = meta["limit"]

        if not laws:
            st.info(
                "No laws found matching your search. "
                "Try different filters."
            )

        else:
            # Calculate number of pages.
            total_pages = (total + limit - 1) // limit
            current_page = st.session_state.page + 1

            st.write(
                f"Found **{total}** matching law(s) — "
                f"Page **{current_page} of {total_pages}**"
            )

            # Build table
            table_rows = []

            for law in laws:
                table_rows.append({
                    "Jurisdiction": law["jurisdiction"]["name"],
                    "Identifier": law["identifier"],
                    "Title": law["title"],
                    "Status": law["status"],
                    "Updated": law["updated_at"],
                    "Source": law["official_url"],
                })

            df = pd.DataFrame(table_rows)

            st.dataframe(
                df,
                column_config={
                    "Source": st.column_config.LinkColumn(
                        "Source",
                        display_text="View bill",
                    ),
                },
                hide_index=True,
            )

            # Pagination controls
            prev_col, page_col, next_col = st.columns([1, 2, 1])

            with prev_col:
                if st.button(
                    "← Previous",
                    disabled=st.session_state.page == 0
                ):
                    st.session_state.page -= 1
                    st.rerun()

            with page_col:
                st.markdown(
                    f"<div style='text-align: center;'>"
                    f"Page {current_page} of {total_pages}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with next_col:
                if st.button(
                    "Next →",
                    disabled=current_page >= total_pages
                ):
                    st.session_state.page += 1
                    st.rerun()

# ----------------------------------------------------------------
# Footer - attribution (required by the API's free tier terms) and
# a disclaimer, since this data is informational, not legal advice.
# ----------------------------------------------------------------

st.divider()
st.caption(
    "Data by [AI Law Tracker](https://ai-law-tracker.com) (CC BY 4.0). "
    "Informational only - not legal advice. Verify against each law's official source link before relying on it."
)
