# Park-Share · Putra Heights

Prototype for the Sime Darby Property University Hackathon 2026 (PEOPLE track).
Commuters book a guaranteed bay near Putra Heights LRT the night before, drawn from a pool of bays whose owners are away.
A retail cap protects shop customers, and every booking carries a tenant-funded breakfast perk.
Serasi residents can list their own bay for the hours they're away, from the Feb 2027 handover target.

> All bays, bookings and street counts are **demo data** until replaced with our field observations.

## Townships

Pick a township in the sidebar of any page. Putra Heights is the pilot. The others are candidates for later roll-out
and show a warning: their numbers are placeholders until we survey them.

| Township | Status | What we actually know |
| --- | --- | --- |
| Putra Heights | Pilot – site visit data, 20 Oct 2026 | See assumptions below |
| Ara Damansara | Candidate – needs site survey | Park & Ride 743 bays (Prasarana figure, 2016); nothing else |
| SJ7 / USJ 7 | Candidate – needs site survey | Nothing yet |

## What's inside

| Page | What it shows |
| --- | --- |
| `app.py` (Home) | The problem and the idea in one screen |
| `pages/1_Commuter.py` | Book a bay → QR code → breakfast perk; café counter redeems perk codes |
| `pages/2_SDP_Admin.py` | Bays offered vs booked, retail-cap slider, revenue, perks redeemed, street-overflow heatmap |
| `pages/3_Simulator.py` | Today vs Putra Point rezoned vs Park-Share, with every assumption as a slider |
| `pages/4_Resident_Host.py` | Serasi residents list a bay (unit, bay, free weekdays and hours, available-from date) and see an illustrative monthly earning |

| Logic | File |
| --- | --- |
| Which commuter gets which bay (retail cap, perimeter rows only, no-show buffer, resident availability dates and weekdays) | `core/allocator.py` |
| Townships, their status and known figures; the sidebar Township picker | `core/sites.py` |
| Busy-shopping-day forecast (Friday, payday, festive) | `core/forecast.py` |
| Morning arrival simulation | `core/simulate.py` |
| SQLite storage and demo bays | `core/db.py` |
| Street counts for the heatmap | `data/field_counts.csv` |

## Run it on your laptop (first time: about 10 minutes)

1. Install **Python 3.11+** from python.org (Windows: tick "Add Python to PATH").
2. Install **Git** and **VS Code**.
3. Open a terminal in this folder and run:

   ```bash
   python -m venv .venv
   # Windows:      .venv\Scripts\activate
   # Mac / Linux:  source .venv/bin/activate
   pip install -r requirements.txt
   streamlit run app.py
   ```

4. Your browser opens at `http://localhost:8501`. Try: Commuter → book → SDP Admin → see it appear.
   Or: Resident Host → list a bay → Commuter → book a weekday in March 2027 (a November 2026 booking won't use it).

After changing anything in `core/`, stop Streamlit (Ctrl+C) and start it again so it loads the new code.
If you change the database layout, also delete `data/parkshare.db` so it rebuilds.

Quick logic check without Streamlit: `python -m core.simulate` prints the four scenarios.

## Put it online (needed for the submission link)

1. Create a **public** GitHub repo and upload this folder (or `git push`). Don't upload `.venv` or `data/parkshare.db`.
2. Go to share.streamlit.io → sign in with GitHub → **New app** → pick the repo → main file `app.py` → Deploy.
3. Open the link in an incognito window to confirm judges can see it.

## Plugging in real data (do this after the site visit)

- **Street heatmap:** replace the rows in `data/field_counts.csv`. Keep the column names; set `source` to `FIELD`.
- **Simulator defaults:** change the numbers in `Scenario` (`core/simulate.py`) to your counts: commuter cars, peak time, Putra Point usage.
- **Bays:** edit `SEED_BAYS` in `core/db.py` to match the zones you found, then delete `data/parkshare.db` so it reseeds.

## Ideas to add if you have time (pick at most one)

- Carpool-to-station credit: two people in one car pay less.
- Plate entry instead of QR (a text field now; camera recognition later).
- Map view of zones with `st.map` or pydeck.
- Bahasa Malaysia toggle on the Commuter page.

## Assumptions to state in the pitch

- Park & Ride capacity 452 bays (Prasarana, 2016); Putra Point lot 600 bays (reported February 2026).
- Arrival curve, Putra Point usage shares and adoption rate are assumptions until calibrated with field counts and the survey.
- Serasi resident bays go live from 1 Feb 2027: the handover **target**, not a confirmed date.
- Resident earning (60% host share × RM5 × 22 working days ≈ RM66/month) is illustrative. The host share isn't agreed with SDP and a bay won't be booked every day.
- Ara Damansara Park & Ride 743 bays (Prasarana, 2016). Every other candidate-site number is a placeholder copied from Putra Heights.
- The forecast is rule-based by design: simple, explainable, and replaceable with a trained model once real booking history exists.
