# Park-Share · project context for Claude Code

## What this is
Prototype for the Sime Darby Property (SDP) University Hackathon 2026 "Township of Tomorrow", PEOPLE track.
Team of 4–5 first-time hackathon students. I am the developer and new to this, so explain what you change in plain words.

**Problem:** Putra Heights LRT station (Kelana Jaya + Sri Petaling interchange) has a 452-bay Park & Ride lot that fills every weekday morning.
Overflow commuters use the 600-bay Putra Point open-air lot (shared with shops) and park illegally on residential streets.
MBSJ's Draft Local Plan 2035 proposes rezoning the Putra Point lot, and SDP is building Putra Heights Sentral (a 25-acre TOD, first phase Serasi Residences, 400 m covered walkway to the station).

**Solution:** Park-Share pools bays that sit empty while their owners are away (SDP land, Serasi resident bays, perimeter retail bays),
lets commuters book a guaranteed bay the night before, protects shop customers with a retail cap (max 30–40% of retail bays, perimeter rows only, lower on busy days),
and attaches a tenant-funded breakfast perk to each booking.

## Deadlines
- Feature freeze: Tue 20 Oct 2026
- Submission: Fri 23 Oct 2026 (aim for noon). Needs a public GitHub repo + live Streamlit Community Cloud link + 5-min demo video.

## How the code is organised
- `app.py` home page; `pages/1_Commuter.py` booking + QR + perk; `pages/2_SDP_Admin.py` dashboard; `pages/3_Simulator.py` scenarios
- `core/allocator.py` bay assignment rules · `core/forecast.py` busy-day rules · `core/simulate.py` morning simulation · `core/db.py` SQLite + demo bays
- `data/field_counts.csv` street counts (SAMPLE until our site visit)
- Run: activate `.venv`, then `streamlit run app.py`. Quick logic check: `python -m core.simulate`

## Rules for changes
- Keep it simple: Streamlit + pandas + plotly + SQLite. No new frameworks, no login system, no paid APIs.
- Never invent numbers. Anything not from our field counts or a cited source must be labelled as an assumption or demo data in the UI.
- Small changes, one at a time. After each change, run the app or `python -m core.simulate` to check it works.
- Ask before deleting files or installing new packages.
- Prefer demo polish (clear labels, good charts, a smooth booking flow) over new features.

## Nice-to-have ideas (only if core is solid)
1. Carpool-to-station credit (cheaper price for 2+ people per car)
2. Map of zones (st.map or pydeck)
3. Bahasa Malaysia toggle on the Commuter page
