import pandas as pd
import plotly.express as px
import streamlit as st

from core.simulate import Scenario, simulate
from core.sites import SITES, scenario_values, site_picker

st.set_page_config(page_title="Simulator · Park-Share", page_icon="📈", layout="wide")
site = site_picker()
v, placeholders = scenario_values(site)
lot = "Putra Point" if site == "putra_heights" else "Shared retail lot"
st.title(f"📈 Morning simulator · {SITES[site]['name']}")
st.caption("Every default is an assumption. Set the sliders to your field counts before quoting any result.")

with st.sidebar:
    st.header("Inputs")
    if SITES[site]["candidate"]:
        known = [f"{k} = {SITES[site]['values'][k]} ({src})" for k, src in SITES[site]["sources"].items()]
        st.caption("Known: " + ("; ".join(known) if known else "nothing yet") +
                   ". Every other input is a PLACEHOLDER copied from Putra Heights.")
    cars = st.slider("Commuter cars per morning", 300, 1200, v["commuter_cars"], 10)
    peak_h = st.slider("Peak arrival time (minutes after 6:00)", 30, 150, v["peak_minute"] - 6 * 60, 5)
    spread = st.slider("Rush spread (minutes)", 10, 60, v["spread_minutes"], 5)
    pr = st.number_input("Park & Ride bays", 0, 2000, v["park_and_ride_bays"])
    pp = st.number_input(f"{lot} bays", 0, 2000, v["putra_point_bays"])
    busy = st.slider(f"{lot} used by non-commuters in morning", 0.0, 1.0, v["putra_point_busy_share"], 0.05)
    noon = st.slider(f"{lot} shoppers need at noon", 0.0, 1.0, v["noon_shopper_share"], 0.05)
    pool = st.slider("Park-Share pooled bays", 0, 300, 30, 5)
    adoption = st.slider("Overflow commuters who book via Park-Share", 0.0, 1.0, v["adoption"], 0.05)

base = dict(commuter_cars=cars, peak_minute=6 * 60 + peak_h, spread_minutes=spread,
            park_and_ride_bays=pr, putra_point_bays=pp, putra_point_busy_share=busy,
            noon_shopper_share=noon, adoption=adoption)
scenarios = {
    "Today": Scenario(**base, pool_bays=0),
    f"{lot} rezoned": Scenario(**{**base, "putra_point_bays": 0}, pool_bays=0),
    "Park-Share": Scenario(**base, pool_bays=pool),
    "Rezoned + Park-Share": Scenario(**{**base, "putra_point_bays": 0}, pool_bays=pool),
}

rows, timelines = [], {}
for name, sc in scenarios.items():
    tl, s = simulate(sc)
    timelines[name] = tl
    rows.append({"Scenario": name, "P&R full at": s["park_and_ride_full_at"] or "never",
                 "Overflow cars": s["overflow"], "In pooled bays": s["pool"],
                 f"In {lot}": s["putra_point"], "On the street": s["street"],
                 f"{lot} free at noon": s["putra_point_free_at_noon"]})
summary = pd.DataFrame(rows)

st.subheader("Scenario comparison")
st.dataframe(summary, hide_index=True)
st.caption(f"'{lot} free at noon' below zero means shoppers can't find a bay.")

st.plotly_chart(px.bar(summary, x="Scenario", y="On the street", text="On the street",
                       title="Cars left on residential streets"))

choice = st.selectbox("Morning timeline for", list(timelines))
tl = timelines[choice].melt(id_vars=["slot", "time"], var_name="where", value_name="cars")
st.plotly_chart(px.line(tl, x="time", y="cars", color="where", markers=True,
                        title=f"Where cars end up as the morning goes on — {choice}"))
