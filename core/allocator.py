"""Decides which commuter gets which bay.

Rules (the 'retail protection' promise on slide 4):
1. Non-retail bays (SDP land, resident hosts) are used first.
2. Retail bays: only 'perimeter' rows, and only up to the retail cap.
3. The cap shrinks on busy shopping days (shopper_peak_ratio from the forecast).
4. A small buffer is held back for no-shows and hosts who return early.
"""
from dataclasses import dataclass


@dataclass
class Bay:
    id: str
    zone: str
    kind: str        # "sdp_land" | "resident" | "retail"
    row: str = ""    # "perimeter" | "storefront" (retail only)


def usable_bays(bays: list[Bay], retail_cap_pct: float, shopper_peak_ratio: float = 0.0,
                buffer_pct: float = 0.05) -> list[Bay]:
    """Bays that may be offered to commuters on a given day, best first."""
    non_retail = [b for b in bays if b.kind != "retail"]
    retail_all = [b for b in bays if b.kind == "retail"]
    perimeter = [b for b in retail_all if b.row == "perimeter"]
    # Cap is a share of ALL retail bays, reduced on busy shopping days.
    retail_limit = int(len(retail_all) * retail_cap_pct * (1 - shopper_peak_ratio))
    pool = non_retail + perimeter[:retail_limit]
    keep = int(round(len(pool) * (1 - buffer_pct)))
    return pool[:keep]


def allocate(request_ids: list[str], bays: list[Bay], taken: set[str], retail_cap_pct: float,
             shopper_peak_ratio: float = 0.0, buffer_pct: float = 0.05):
    """Assign free bays to requests in order. Returns (assigned dict, waitlist)."""
    free = [b for b in usable_bays(bays, retail_cap_pct, shopper_peak_ratio, buffer_pct) if b.id not in taken]
    assigned = {rid: bay for rid, bay in zip(request_ids, free)}
    waitlist = request_ids[len(free):]
    return assigned, waitlist
