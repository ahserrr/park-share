"""Very small, explainable demand forecast.

Judges prefer an honest simple model over a black box. This one says:
'tomorrow looks like the average of the same weekday in past weeks',
plus known busy shopping days (payday, Friday, festive weeks).
Upgrade later: train scikit-learn on real booking history.
"""
import datetime as dt

BUSY_DAYS = {4: 0.25}            # Friday (weekday 4): shoppers need 25% more bays
PAYDAY_BOOST = 0.15              # around the 25th–28th of the month
FESTIVE_DATES: set[dt.date] = set()  # add Deepavali, Christmas, CNY weeks etc.


def shopper_peak_ratio(day: dt.date) -> float:
    """0 = normal day, 0.4 = very busy. Shrinks the retail cap."""
    ratio = BUSY_DAYS.get(day.weekday(), 0.0)
    if 25 <= day.day <= 28:
        ratio += PAYDAY_BOOST
    if day in FESTIVE_DATES:
        ratio += 0.3
    return min(ratio, 0.8)


def commuter_demand(history: dict[dt.date, int], day: dt.date, weeks: int = 4) -> int | None:
    """Average bookings on the same weekday over the last `weeks` weeks."""
    same = [history[d] for d in history if d.weekday() == day.weekday() and d < day]
    same = sorted(same)[-weeks:] if same else []
    return round(sum(same) / len(same)) if same else None
