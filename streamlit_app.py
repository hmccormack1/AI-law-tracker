import pandas as pd
import requests
import streamlit as st

from law_tracker import get_laws, API_KEY

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

# ----------------------------------------------------------------
# Load the list of US jurisdictions (all 50 states + US-Federal) once per
# session, so the dropdown below has real options instead of free text.
# @st.cache_data means this only actually calls the API the first time -
# later reruns reuse the cached result instead of hitting the API again.
# ----------------------------------------------------------------

@st.cache_data
def load_us_jurisdictions():
    url = "https://ai-law-tracker.com/api/v1/jurisdictions"
    headers = {"X-API-Key": API_KEY}
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

if go:
    if not selected_names:
        st.warning("Please select at least one state or US-Federal first.")
    else:
        # Turn the friendly names the user picked back into the slugs the
        # API expects. Passing a list here searches all of them at once.
        selected_slugs = [name_to_slug[name] for name in selected_names]

        result = get_laws(
            jurisdiction=selected_slugs,
            status=status.strip(),
            keyword=keyword.strip(),
        )

        if result is None:
            st.error("Something went wrong calling the API. Check your API key or inputs and try again.")
        else:
            laws = result["data"]
            total = result["meta"]["total"]

            if not laws:
                st.info("No laws found matching your search. Try different filters.")
            else:
                st.write(f"Found **{total}** matching law(s):")

                # Build a simple table with just the columns we care about.
                # The nested "jurisdiction" field is a dict, so we pull out
                # just its "name" to keep the table flat and readable.
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

                # create a streamlit dataframe from the flattened API response
                # use Streamlit's new column_config feature to make the "Source" column a clickable link
                st.dataframe(
                    df,
                    column_config={
                        "Source": st.column_config.LinkColumn("Source", display_text="View bill"),
                    },
                    hide_index=True,
                )

# ----------------------------------------------------------------
# Footer - attribution (required by the API's free tier terms) and
# a disclaimer, since this data is informational, not legal advice.
# ----------------------------------------------------------------

st.divider()
st.caption(
    "Data by [AI Law Tracker](https://ai-law-tracker.com) (CC BY 4.0). "
    "Informational only - not legal advice. Verify against each law's official source link before relying on it."
)
