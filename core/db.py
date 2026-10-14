"""SQLite storage: bays, bookings, settings. Seeded with DEMO data."""
import datetime as dt
import secrets
import sqlite3
from pathlib import Path

from core.allocator import Bay

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "parkshare.db"

# DEMO bays. Replace zone names and counts with what you find on site.
SEED_BAYS = (
    [Bay(f"L{i:02d}", "PHS land (interim)", "sdp_land") for i in range(1, 13)]
    + [Bay(f"R{i:02d}", "Serasi resident hosts", "resident") for i in range(1, 9)]
    + [Bay(f"P{i:02d}", "Retail perimeter", "retail", "perimeter") for i in range(1, 11)]
    + [Bay(f"S{i:02d}", "Retail storefront", "retail", "storefront") for i in range(1, 11)]
)


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript("""
        CREATE TABLE IF NOT EXISTS bays (id TEXT PRIMARY KEY, zone TEXT, kind TEXT, row TEXT);
        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY, day TEXT, commuter TEXT, bay_id TEXT,
            perk_code TEXT, perk_redeemed INTEGER DEFAULT 0, price REAL, created TEXT);
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
    """)
    if con.execute("SELECT COUNT(*) FROM bays").fetchone()[0] == 0:
        con.executemany("INSERT INTO bays VALUES (?,?,?,?)",
                        [(b.id, b.zone, b.kind, b.row) for b in SEED_BAYS])
        con.executemany("INSERT INTO settings VALUES (?,?)",
                        [("retail_cap_pct", "0.35"), ("price", "5.0")])
        con.commit()
    return con


def get_bays(con) -> list[Bay]:
    return [Bay(r["id"], r["zone"], r["kind"], r["row"] or "") for r in con.execute("SELECT * FROM bays")]


def get_setting(con, key: str, default: str) -> str:
    row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(con, key: str, value) -> None:
    con.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, str(value)))
    con.commit()


def taken_bays(con, day: dt.date) -> set[str]:
    return {r["bay_id"] for r in con.execute("SELECT bay_id FROM bookings WHERE day=?", (day.isoformat(),))}


def add_booking(con, day: dt.date, commuter: str, bay_id: str, price: float) -> dict:
    booking = {
        "id": "PS-" + secrets.token_hex(3).upper(),
        "day": day.isoformat(), "commuter": commuter, "bay_id": bay_id,
        "perk_code": "PERK-" + secrets.token_hex(2).upper(),
        "price": price, "created": dt.datetime.now().isoformat(timespec="seconds"),
    }
    con.execute("INSERT INTO bookings (id, day, commuter, bay_id, perk_code, price, created) "
                "VALUES (:id,:day,:commuter,:bay_id,:perk_code,:price,:created)", booking)
    con.commit()
    return booking


def bookings(con, day: dt.date | None = None) -> list[sqlite3.Row]:
    if day:
        return con.execute("SELECT b.*, y.zone, y.kind FROM bookings b JOIN bays y ON y.id=b.bay_id "
                           "WHERE day=? ORDER BY created", (day.isoformat(),)).fetchall()
    return con.execute("SELECT b.*, y.zone, y.kind FROM bookings b JOIN bays y ON y.id=b.bay_id "
                       "ORDER BY day, created").fetchall()


def redeem_perk(con, code: str) -> bool:
    cur = con.execute("UPDATE bookings SET perk_redeemed=1 WHERE perk_code=? AND perk_redeemed=0", (code,))
    con.commit()
    return cur.rowcount == 1


def reset_demo(con) -> None:
    con.execute("DELETE FROM bookings")
    con.commit()
