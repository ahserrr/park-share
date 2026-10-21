"""Decides which commuter gets which bay.

Rules (the 'retail protection' promise on slide 4):
1. Non-retail bays (SDP land, resident hosts) are used first.
2. Retail bays: only 'perimeter' rows, and only up to the retail cap.
3. The cap shrinks on busy shopping days (shopper_peak_ratio from the forecast).
4. A small buffer is held back for no-shows and hosts who return early.
5. Resident bays only count from their 'available from' date, and only on the weekdays listed.
"""
import datetime as dt
from dataclasses import dataclass


@dataclass
class Bay:
    id: str
    zone: str
    kind: str        # "sdp_land" | "resident" | "retail"
    row: str = ""    # "perimeter" | "storefront" (retail only)
    site: str = "putra_heights"
    unit: str = ""            # resident only: owner's unit number
    weekdays: str = ""        # resident only: "0,1,2" = Mon, Tue, Wed free ("" = every day)
    from_time: str = ""       # resident only: "07:00"
    to_time: str = ""         # resident only: "19:00"
    available_from: str = ""  # resident only: ISO date, e.g. "2027-02-01"


def is_open_on(bay: Bay, day: dt.date) -> bool:
    """False if a resident bay is not yet available, or its owner hasn't listed that weekday."""
    if bay.kind != "resident":
        return True
    if bay.available_from and day < dt.date.fromisoformat(bay.available_from):
        return False
    if bay.weekdays and day.weekday() not in {int(d) for d in bay.weekdays.split(",")}:
        return False
    return True


def usable_bays(bays: list[Bay], day: dt.date, retail_cap_pct: float, shopper_peak_ratio: float = 0.0,
                buffer_pct: float = 0.05) -> list[Bay]:
    """Bays that may be offered to commuters on a given day, best first."""
    non_retail = [b for b in bays if b.kind != "retail" and is_open_on(b, day)]
    retail_all = [b for b in bays if b.kind == "retail"]
    perimeter = [b for b in retail_all if b.row == "perimeter"]
    # Cap is a share of ALL retail bays, reduced on busy shopping days.
    retail_limit = int(len(retail_all) * retail_cap_pct * (1 - shopper_peak_ratio))
    pool = non_retail + perimeter[:retail_limit]
    keep = int(round(len(pool) * (1 - buffer_pct)))
    return pool[:keep]


def allocate(request_ids: list[str], bays: list[Bay], taken: set[str], day: dt.date, retail_cap_pct: float,
             shopper_peak_ratio: float = 0.0, buffer_pct: float = 0.05):
    """Assign free bays to requests in order. Returns (assigned dict, waitlist)."""
    free = [b for b in usable_bays(bays, day, retail_cap_pct, shopper_peak_ratio, buffer_pct)
            if b.id not in taken]
    assigned = {rid: bay for rid, bay in zip(request_ids, free)}
    waitlist = request_ids[len(free):]
    return assigned, waitlist
