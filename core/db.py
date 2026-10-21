"""SQLite storage: bays, bookings, settings. Seeded with DEMO data (Putra Heights only)."""
import datetime as dt
import secrets
import sqlite3
from dataclasses import astuple
from pathlib import Path

from core.allocator import Bay

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "parkshare.db"

# DEMO bays for the pilot site. Replace zone names and counts with what you find on site.
# Resident bays are not seeded: Serasi residents list their own on the Resident Host page.
SEED_BAYS = (
    [Bay(f"L{i:02d}", "PHS land (interim)", "sdp_land") for i in range(1, 13)]
    + [Bay(f"P{i:02d}", "Retail perimeter", "retail", "perimeter") for i in range(1, 11)]
    + [Bay(f"S{i:02d}", "Retail storefront", "retail", "storefront") for i in range(1, 11)]
)
BAY_COLUMNS = "id, zone, kind, row, site, unit, weekdays, from_time, to_time, available_from"


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript("""
        CREATE TABLE IF NOT EXISTS bays (
            id TEXT PRIMARY KEY, zone TEXT, kind TEXT, row TEXT, site TEXT,
            unit TEXT, weekdays TEXT, from_time TEXT, to_time TEXT, available_from TEXT);
        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY, site TEXT, day TEXT, commuter TEXT, bay_id TEXT,
            perk_code TEXT, perk_redeemed INTEGER DEFAULT 0, price REAL, created TEXT);
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
    """)
    if con.execute("SELECT COUNT(*) FROM bays WHERE site='putra_heights'").fetchone()[0] == 0:
        con.executemany(f"INSERT INTO bays ({BAY_COLUMNS}) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        [astuple(b) for b in SEED_BAYS])
        con.executemany("INSERT OR IGNORE INTO settings VALUES (?,?)",
                        [("retail_cap_pct", "0.35"), ("price", "5.0")])
        con.commit()
    return con


def get_bays(con, site: str) -> list[Bay]:
    rows = con.execute(f"SELECT {BAY_COLUMNS} FROM bays WHERE site=? ORDER BY rowid", (site,))
    return [Bay(*(v or "" for v in r)) for r in rows]


def add_resident_bay(con, unit: str, bay_no: str, weekdays: list[int], from_time: dt.time,
                     to_time: dt.time, available_from: dt.date, site: str = "putra_heights") -> Bay:
    """Save (or update) a resident's listing. Same unit + bay number = same listing."""
    bay = Bay(f"{unit}/{bay_no}", "Serasi resident hosts", "resident", "", site, unit,
              ",".join(str(d) for d in sorted(weekdays)),
              from_time.strftime("%H:%M"), to_time.strftime("%H:%M"), available_from.isoformat())
    con.execute(f"INSERT OR REPLACE INTO bays ({BAY_COLUMNS}) VALUES (?,?,?,?,?,?,?,?,?,?)", astuple(bay))
    con.commit()
    return bay


def get_setting(con, key: str, default: str) -> str:
    row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(con, key: str, value) -> None:
    con.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, str(value)))
    con.commit()


def taken_bays(con, day: dt.date) -> set[str]:
    return {r["bay_id"] for r in con.execute("SELECT bay_id FROM bookings WHERE day=?", (day.isoformat(),))}


def add_booking(con, site: str, day: dt.date, commuter: str, bay_id: str, price: float) -> dict:
    booking = {
        "id": "PS-" + secrets.token_hex(3).upper(), "site": site,
        "day": day.isoformat(), "commuter": commuter, "bay_id": bay_id,
        "perk_code": "PERK-" + secrets.token_hex(2).upper(),
        "price": price, "created": dt.datetime.now().isoformat(timespec="seconds"),
    }
    con.execute("INSERT INTO bookings (id, site, day, commuter, bay_id, perk_code, price, created) "
                "VALUES (:id,:site,:day,:commuter,:bay_id,:perk_code,:price,:created)", booking)
    con.commit()
    return booking


def bookings(con, site: str, day: dt.date | None = None) -> list[sqlite3.Row]:
    query = "SELECT b.*, y.zone, y.kind FROM bookings b JOIN bays y ON y.id=b.bay_id WHERE b.site=?"
    if day:
        return con.execute(query + " AND day=? ORDER BY created", (site, day.isoformat())).fetchall()
    return con.execute(query + " ORDER BY day, created", (site,)).fetchall()


def redeem_perk(con, code: str) -> bool:
    cur = con.execute("UPDATE bookings SET perk_redeemed=1 WHERE perk_code=? AND perk_redeemed=0", (code,))
    con.commit()
    return cur.rowcount == 1


def reset_demo(con) -> None:
    con.execute("DELETE FROM bookings")
    con.commit()
