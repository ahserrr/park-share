import datetime as dt

import pandas as pd
import streamlit as st

from core import db
from core.sites import site_picker

st.set_page_config(page_title="Resident Host · Park-Share", page_icon="🏠")
site = site_picker()
con = db.connect()
price = float(db.get_setting(con, "price", "5.0"))

st.title("🏠 List your Serasi bay")
st.caption("Away at work during the day? Let a commuter use your bay while you're out.")
if site != "putra_heights":
    st.info("Resident hosting is only open to Serasi Residences at Putra Heights for now.")
    st.stop()

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HANDOVER = dt.date(2027, 2, 1)

with st.form("host"):
    c1, c2 = st.columns(2)
    unit = c1.text_input("Unit number", placeholder="e.g. A-12-03")
    bay_no = c2.text_input("Bay number", placeholder="e.g. B2-045")
    days = st.multiselect("Weekdays your bay is free", DAYS, default=DAYS[:5])
    t1, t2 = st.columns(2)
    from_time = t1.time_input("Free from", dt.time(7, 0))
    to_time = t2.time_input("Free until", dt.time(19, 0))
    available_from = st.date_input("Available from (Serasi handover target, Feb 2027)", value=HANDOVER)
    submitted = st.form_submit_button("List my bay", type="primary")

if submitted:
    if not unit.strip() or not bay_no.strip() or not days:
        st.error("Please fill in unit number, bay number and at least one weekday.")
    elif from_time >= to_time:
        st.error("'Free until' must be later than 'Free from'.")
    else:
        bay = db.add_resident_bay(con, unit.strip().upper(), bay_no.strip().upper(),
                                  [DAYS.index(d) for d in days], from_time, to_time, available_from)
        st.success(f"Listed bay **{bay.id}**. Commuters can book it from {available_from:%d %b %Y} "
                   f"on {', '.join(days)}.")

# --- Illustrative earning -----------------------------------------------------
HOST_SHARE, DAYS_PER_MONTH = 0.60, 22
st.subheader("💰 What you could earn")
st.metric("Illustrative monthly earning", f"RM{HOST_SHARE * price * DAYS_PER_MONTH:.0f}")
st.caption(f"{HOST_SHARE:.0%} host share × RM{price:.0f} per booking × {DAYS_PER_MONTH} working days. "
           "ASSUMPTIONS for illustration: host share and booking rate are not agreed with SDP, "
           "and a bay is not booked every day.")

# --- Current listings ---------------------------------------------------------
listings = [b for b in db.get_bays(con, site) if b.kind == "resident"]
st.subheader("Listed resident bays")
if not listings:
    st.caption("No bays listed yet.")
else:
    st.dataframe(pd.DataFrame([{
        "bay": b.id, "free on": ", ".join(DAYS[int(d)] for d in b.weekdays.split(",")),
        "hours": f"{b.from_time}–{b.to_time}", "available from": b.available_from,
    } for b in listings]), hide_index=True)
