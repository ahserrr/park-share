"""Park-Share — run with:  streamlit run app.py"""
import streamlit as st

from core.sites import site_picker

st.set_page_config(page_title="Park-Share Putra Heights", page_icon="🅿️", layout="wide")
site_picker()

st.title("Park-Share · Putra Heights")
st.caption("SDP University Hackathon 2026 · PEOPLE track · prototype with demo data")

st.markdown("""
**The problem.** Putra Heights LRT station's 452-bay Park & Ride lot fills every weekday morning.
Overflow cars spill into the shared Putra Point lot and onto residential streets.

**The idea.** Pool bays that sit empty while their owners are away, let commuters book one the night before,
protect shop customers with a retail cap, and turn every booking into a breakfast sale for a local tenant.

Use the pages on the left:
1. **Commuter** — book tomorrow's bay, get a QR code and a breakfast perk.
2. **SDP Admin** — occupancy, retail-cap control, revenue, perk redemptions.
3. **Simulator** — test today vs. rezoning vs. Park-Share with your own field numbers.
4. **Resident Host** — Serasi residents list their bay for the hours they're away.

Use the **Township** dropdown on the left to switch sites. Putra Heights is the pilot;
other townships are candidates we have not surveyed yet.
""")
st.info("All bays, bookings and counts in this prototype are DEMO data until replaced with field observations.")
