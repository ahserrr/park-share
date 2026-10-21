"""Townships Park-Share could run in. Only Putra Heights has our own field data.

A value missing from a site's "values" is UNKNOWN. The simulator fills it with the
Putra Heights number as a placeholder and the UI must say so.
"""
from dataclasses import asdict

from core.simulate import Scenario

PILOT = "putra_heights"
PLACEHOLDER_WARNING = "No field data yet – values are placeholders until we survey this site."

SITES = {
    "putra_heights": {
        "name": "Putra Heights",
        "status": "Pilot – site visit data, 20 Oct 2026",
        "candidate": False,
        "values": asdict(Scenario()),
        "sources": {},
    },
    "ara_damansara": {
        "name": "Ara Damansara",
        "status": "Candidate – needs site survey",
        "candidate": True,
        "values": {"park_and_ride_bays": 743},
        "sources": {"park_and_ride_bays": "Prasarana figure, 2016"},
    },
    "sj7_usj7": {
        "name": "SJ7 / USJ 7",
        "status": "Candidate – needs site survey",
        "candidate": True,
        "values": {},
        "sources": {},
    },
}


def scenario_values(site_key: str) -> tuple[dict, list[str]]:
    """Simulator inputs for a site, plus the names of fields that are placeholders."""
    known = SITES[site_key]["values"]
    pilot = SITES[PILOT]["values"]
    placeholders = [k for k in pilot if k not in known]
    return {**pilot, **known}, placeholders


def site_picker() -> str:
    """Township dropdown in the sidebar. Remembers the choice across pages."""
    import streamlit as st

    def remember():
        st.session_state["site"] = st.session_state["_site_widget"]

    # Streamlit forgets a widget's own key when you change page, so the choice lives in
    # "site" and is copied into the dropdown at the start of every run.
    st.session_state.setdefault("site", PILOT)
    st.session_state["_site_widget"] = st.session_state["site"]
    st.sidebar.selectbox("Township", list(SITES), key="_site_widget",
                         format_func=lambda k: SITES[k]["name"], on_change=remember)
    site = st.session_state["site"]
    st.sidebar.caption(f"Status: {SITES[site]['status']}")
    if SITES[site]["candidate"]:
        st.warning(PLACEHOLDER_WARNING)
    return site
