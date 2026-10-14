import datetime as dt
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from core import db
from core.allocator import usable_bays
from core.forecast import shopper_peak_ratio

st.set_page_config(page_title="SDP Admin · Park-Share", page_icon="🏢", layout="wide")
con = db.connect()
st.title("🏢 SDP Admin dashboard")

day = st.date_input("Day", value=dt.date.today() + dt.timedelta(days=1))
bays = db.get_bays(con)
peak = shopper_peak_ratio(day)

# --- Controls -------------------------------------------------------------
c1, c2 = st.columns(2)
cap = c1.slider("Retail cap: max share of retail bays commuters may use", 0.0, 0.4,
                float(db.get_setting(con, "retail_cap_pct", "0.35")), 0.05)
price = c2.number_input("Price per booking (RM)", 1.0, 20.0, float(db.get_setting(con, "price", "5.0")), 0.5)
if st.button("Save settings"):
    db.set_setting(con, "retail_cap_pct", cap)
    db.set_setting(con, "price", price)
    st.success("Saved.")

offered = usable_bays(bays, cap, peak)
day_bookings = db.bookings(con, day)
retail_total = sum(b.kind == "retail" for b in bays)
retail_offered = sum(b.kind == "retail" for b in offered)

# --- KPIs -----------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Bays offered", len(offered), help="After retail cap, busy-day adjustment and no-show buffer")
k2.metric("Booked", len(day_bookings))
k3.metric("Retail bays kept for shoppers", retail_total - retail_offered, f"of {retail_total}")
k4.metric("Revenue (RM)", f"{sum(r['price'] for r in day_bookings):.2f}")
if peak:
    st.info(f"Busy shopping day detected (peak ratio {peak:.0%}): retail cap automatically reduced.")

# --- Occupancy by zone ----------------------------------------------------
zones = pd.DataFrame([{"zone": b.zone, "offered": 1} for b in offered]).groupby("zone").sum()
booked = pd.DataFrame([{"zone": r["zone"], "booked": 1} for r in day_bookings])
booked = booked.groupby("zone").sum() if not booked.empty else pd.DataFrame(columns=["booked"])
occ = zones.join(booked, how="left").fillna(0).astype(int).reset_index()
occ["occupancy %"] = (occ["booked"] / occ["offered"] * 100).round(0)
st.subheader("Occupancy by zone")
st.plotly_chart(px.bar(occ, x="zone", y=["offered", "booked"], barmode="group"))

# --- Street overflow heatmap from field counts ----------------------------
st.subheader("Street overflow heatmap (share with MBSJ / SDP security)")
counts_file = Path(__file__).resolve().parent.parent / "data" / "field_counts.csv"
counts = pd.read_csv(counts_file)
if (counts["source"] == "SAMPLE").any():
    st.warning("Showing SAMPLE numbers. Replace data/field_counts.csv with your real site-visit counts.")
heat = counts.pivot_table(index="segment", columns="time", values="cars_parked_illegally", aggfunc="sum")
st.plotly_chart(px.imshow(heat, text_auto=True, aspect="auto", color_continuous_scale="Reds",
                          labels={"color": "cars"}))

# --- Bookings table -------------------------------------------------------
st.subheader("Bookings")
table = pd.DataFrame([dict(r) for r in day_bookings])
if table.empty:
    st.caption("No bookings yet for this day. Make one on the Commuter page.")
else:
    st.dataframe(table[["id", "commuter", "bay_id", "zone", "price", "perk_redeemed"]], hide_index=True)
    st.metric("Perks redeemed (tenant sales driven)", int(table["perk_redeemed"].sum()))

if st.button("Reset demo bookings"):
    db.reset_demo(con)
    st.rerun()
