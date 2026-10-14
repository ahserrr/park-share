"""Morning simulation: commuter cars arriving at Putra Heights LRT.

Every default here is an ASSUMPTION. Replace them with your own field counts
(data/field_counts.csv) before you put any result on a slide.
"""
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd


@dataclass
class Scenario:
    commuter_cars: int = 700          # cars wanting to park for the LRT each morning (calibrate!)
    peak_minute: int = 7 * 60 + 15    # minutes after midnight when arrivals peak (07:15)
    spread_minutes: int = 35          # how wide the morning rush is (std. deviation)
    park_and_ride_bays: int = 452     # Prasarana lot (published figure, 2016)
    putra_point_bays: int = 600       # open-air lot shared by shops and commuters (reported Feb 2026)
    putra_point_busy_share: float = 0.65  # share of Putra Point already used by non-commuters in the morning
    noon_shopper_share: float = 0.70      # share of Putra Point that shoppers need at noon
    pool_bays: int = 0                # Park-Share pooled bays (0 = today, no Park-Share)
    adoption: float = 0.6             # share of overflow commuters who book through Park-Share
    seed: int = 7


def simulate(s: Scenario) -> tuple[pd.DataFrame, dict]:
    """Return (timeline per 15-minute slot, summary numbers)."""
    rng = np.random.default_rng(s.seed)
    arrivals = rng.normal(s.peak_minute, s.spread_minutes, s.commuter_cars)
    arrivals = np.sort(np.clip(arrivals, 6 * 60, 10 * 60 - 1)).astype(int)
    uses_app = rng.random(s.commuter_cars) < s.adoption

    pr_free = s.park_and_ride_bays
    pp_free = int(s.putra_point_bays * (1 - s.putra_point_busy_share))
    pool_free = s.pool_bays
    counts = {"park_and_ride": 0, "putra_point": 0, "pool": 0, "street": 0}
    pr_full_at = None
    rows = []

    for minute, app in zip(arrivals, uses_app):
        if pr_free > 0:
            pr_free -= 1
            where = "park_and_ride"
            if pr_free == 0:
                pr_full_at = minute
        elif app and pool_free > 0:
            pool_free -= 1
            where = "pool"
        elif pp_free > 0:
            pp_free -= 1
            where = "putra_point"
        else:
            where = "street"
        counts[where] += 1
        rows.append({"minute": minute, "where": where})

    df = pd.DataFrame(rows)
    df["slot"] = (df["minute"] // 15) * 15
    timeline = (
        df.pivot_table(index="slot", columns="where", aggfunc="size", fill_value=0)
        .reindex(columns=["park_and_ride", "pool", "putra_point", "street"], fill_value=0)
        .cumsum()
        .reset_index()
    )
    timeline["time"] = timeline["slot"].map(lambda m: f"{m // 60:02d}:{m % 60:02d}")

    commuters_in_pp = counts["putra_point"]
    noon_free = s.putra_point_bays - commuters_in_pp - int(s.putra_point_bays * s.noon_shopper_share)
    summary = {
        **counts,
        "park_and_ride_full_at": None if pr_full_at is None else f"{pr_full_at // 60:02d}:{pr_full_at % 60:02d}",
        "overflow": s.commuter_cars - counts["park_and_ride"],
        "putra_point_free_at_noon": noon_free,  # negative = shoppers can't find a bay
        "scenario": asdict(s),
    }
    return timeline, summary


if __name__ == "__main__":
    for name, sc in {
        "Today": Scenario(),
        "Putra Point rezoned": Scenario(putra_point_bays=0),
        "Park-Share, 30 bays": Scenario(pool_bays=30),
        "Park-Share, 150 bays": Scenario(pool_bays=150),
    }.items():
        _, out = simulate(sc)
        out.pop("scenario")
        print(f"{name:22s}", out)
