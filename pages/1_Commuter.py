import datetime as dt
import io

import qrcode
import streamlit as st

from core import db
from core.allocator import allocate
from core.forecast import shopper_peak_ratio
from core.sites import SITES, site_picker

st.set_page_config(page_title="Commuter · Park-Share", page_icon="🚇")
site = site_picker()
con = db.connect()
price = float(db.get_setting(con, "price", "5.0"))
cap = float(db.get_setting(con, "retail_cap_pct", "0.35"))
bays = db.get_bays(con, site)

st.title("🚇 Book tomorrow's bay")
st.caption(f"Guaranteed bay within a short walk of {SITES[site]['name']} LRT · includes a breakfast perk")
if not bays:
    st.info(f"Park-Share has no bays at {SITES[site]['name']} yet. Bookings open after we survey the site.")
    st.stop()

tomorrow = dt.date.today() + dt.timedelta(days=1)
with st.form("book"):
    name = st.text_input("Your name or nickname")
    day = st.date_input("Day", value=tomorrow, min_value=dt.date.today())
    submitted = st.form_submit_button(f"Book for RM{price:.2f}", type="primary")

if submitted:
    if not name.strip():
        st.error("Please enter a name.")
    else:
        assigned, waitlist = allocate(["me"], bays, db.taken_bays(con, day), day,
                                      retail_cap_pct=cap, shopper_peak_ratio=shopper_peak_ratio(day))
        if waitlist:
            st.warning("Sorry, the pool is full for that day. You're on the waitlist; "
                       "we'll release unused bays at 10:00 AM.")
        else:
            bay = assigned["me"]
            st.session_state["last"] = db.add_booking(con, site, day, name.strip(), bay.id, price) | {"zone": bay.zone}

booking = st.session_state.get("last")
if booking and booking["site"] == site:
    st.success(f"Booked! Bay **{booking['bay_id']}** in **{booking['zone']}** on {booking['day']}.")
    col1, col2 = st.columns(2)
    with col1:
        img = qrcode.make(f"PARKSHARE|{booking['id']}|{booking['bay_id']}|{booking['day']}")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), caption=f"Scan at the entry stand · {booking['id']}", width=220)
    with col2:
        st.subheader("☕ Your breakfast perk")
        st.markdown(f"Show code **{booking['perk_code']}** at a partner café before 11:00 AM.")
        st.caption("Funded by the café as a customer-acquisition offer, not taken from your parking fee.")
        st.markdown(f"**Walk:** follow the covered walkway to {SITES[site]['name']} LRT station.")

st.divider()
st.subheader("Café counter: redeem a perk")
code = st.text_input("Perk code", placeholder="PERK-XXXX")
if st.button("Redeem"):
    st.success("Perk redeemed ✔") if db.redeem_perk(con, code.strip().upper()) else st.error("Code not valid or already used.")
