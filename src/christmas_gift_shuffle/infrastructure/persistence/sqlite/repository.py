import sqlite3
from pathlib import Path

from ....application.interfaces import GiftExchangeRepository
from ....domain.entities import ExchangeStatus, GiftAssignment, GiftExchange, Participant, Theme
from ....domain.exceptions import ConfigurationError


class SQLiteGiftExchangeRepository(GiftExchangeRepository):
    """SQLite adapter. Each write is transactional; assignments are immutable after generation."""

    def __init__(self, database_path: str | Path = "data/christmas_gift_shuffle.db"):
        self.database_path = Path(database_path)

    def _connect(self):
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.database_path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 15000")
        return conn

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS gift_exchanges (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('draft','generated','closed')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS participants (
                    id TEXT PRIMARY KEY,
                    exchange_id TEXT NOT NULL REFERENCES gift_exchanges(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    UNIQUE(exchange_id, email),
                    UNIQUE(exchange_id, id)
                );
                CREATE TABLE IF NOT EXISTS themes (
                    id TEXT PRIMARY KEY,
                    exchange_id TEXT NOT NULL REFERENCES gift_exchanges(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    UNIQUE(exchange_id, name),
                    UNIQUE(exchange_id, id)
                );
                CREATE TABLE IF NOT EXISTS gift_assignments (
                    id TEXT PRIMARY KEY,
                    exchange_id TEXT NOT NULL REFERENCES gift_exchanges(id) ON DELETE CASCADE,
                    buyer_id TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    theme_id TEXT NOT NULL,
                    CHECK(buyer_id <> recipient_id),
                    FOREIGN KEY(exchange_id, buyer_id) REFERENCES participants(exchange_id, id),
                    FOREIGN KEY(exchange_id, recipient_id) REFERENCES participants(exchange_id, id),
                    FOREIGN KEY(exchange_id, theme_id) REFERENCES themes(exchange_id, id),
                    UNIQUE(exchange_id, buyer_id, theme_id),
                    UNIQUE(exchange_id, recipient_id, theme_id)
                );
                CREATE INDEX IF NOT EXISTS idx_participant_email ON participants(email);
            """)

    def _insert_exchange(self, conn, exchange: GiftExchange) -> None:
        conn.execute(
            "INSERT INTO gift_exchanges(id,name,status) VALUES(?,?,?)",
            (exchange.id, exchange.name, exchange.status.value),
        )
        conn.executemany(
            "INSERT INTO participants(id,exchange_id,name,email) VALUES(?,?,?,?)",
            [(p.id, exchange.id, p.name, p.email) for p in exchange.participants],
        )
        conn.executemany(
            "INSERT INTO themes(id,exchange_id,name,description) VALUES(?,?,?,?)",
            [(t.id, exchange.id, t.name, t.description) for t in exchange.themes],
        )
        if exchange.assignments:
            conn.executemany(
                "INSERT INTO gift_assignments(id,exchange_id,buyer_id,recipient_id,theme_id) VALUES(?,?,?,?,?)",
                [(a.id, exchange.id, a.buyer_id, a.recipient_id, a.theme_id) for a in exchange.assignments],
            )

    def save(self, exchange: GiftExchange) -> None:
        if exchange.status != ExchangeStatus.DRAFT:
            exchange.validate_assignments()
        with self._connect() as conn:
            self._insert_exchange(conn, exchange)

    def save_generated_exchange(self, exchange: GiftExchange) -> None:
        if exchange.status != ExchangeStatus.GENERATED:
            raise ConfigurationError("Only generated exchanges can be saved as generated.")
        exchange.validate_assignments()
        with self._connect() as conn:
            row = conn.execute("SELECT status FROM gift_exchanges WHERE id=?", (exchange.id,)).fetchone()
            if row is None:
                raise KeyError(f"Exchange {exchange.id!r} was not found.")
            if row["status"] != ExchangeStatus.DRAFT.value:
                raise ConfigurationError("Only draft exchanges can be generated.")
            conn.execute("UPDATE gift_exchanges SET status='generated' WHERE id=?", (exchange.id,))
            conn.executemany(
                "INSERT INTO gift_assignments(id,exchange_id,buyer_id,recipient_id,theme_id) VALUES(?,?,?,?,?)",
                [(a.id, exchange.id, a.buyer_id, a.recipient_id, a.theme_id) for a in exchange.assignments],
            )

    def get_by_id(self, exchange_id: str) -> GiftExchange | None:
        with self._connect() as conn:
            e = conn.execute("SELECT id,name,status FROM gift_exchanges WHERE id=?", (exchange_id,)).fetchone()
            if e is None:
                return None
            ps = conn.execute("SELECT id,name,email FROM participants WHERE exchange_id=? ORDER BY rowid", (exchange_id,)).fetchall()
            ts = conn.execute("SELECT id,name,description FROM themes WHERE exchange_id=? ORDER BY rowid", (exchange_id,)).fetchall()
            ass = conn.execute("SELECT id,buyer_id,recipient_id,theme_id FROM gift_assignments WHERE exchange_id=? ORDER BY rowid", (exchange_id,)).fetchall()
        participants = tuple(Participant(r["name"], r["email"], id=r["id"]) for r in ps)
        themes = tuple(Theme(r["name"], r["description"], id=r["id"]) for r in ts)
        assignments = tuple(GiftAssignment(r["buyer_id"], r["recipient_id"], r["theme_id"], id=r["id"]) for r in ass)
        return GiftExchange(
            name=e["name"], participants=participants, themes=themes,
            assignments=assignments, status=ExchangeStatus(e["status"]), id=e["id"]
        )

    def list_exchanges(self) -> list[GiftExchange]:
        with self._connect() as conn:
            rows = conn.execute("SELECT id FROM gift_exchanges ORDER BY created_at DESC,rowid DESC").fetchall()
        return [self.get_by_id(row["id"]) for row in rows]

    def get_by_participant_email(self, email: str) -> list[GiftExchange]:
        normalized = email.strip().casefold()
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT e.id FROM gift_exchanges e
                   JOIN participants p ON p.exchange_id=e.id
                   WHERE p.email=? AND e.status='generated'
                   ORDER BY e.created_at DESC""", (normalized,)
            ).fetchall()
        return [self.get_by_id(row["id"]) for row in rows]

    def delete_draft(self, exchange_id: str) -> None:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM gift_exchanges WHERE id=? AND status='draft'", (exchange_id,))
            if cur.rowcount == 0:
                exists = conn.execute("SELECT 1 FROM gift_exchanges WHERE id=?", (exchange_id,)).fetchone()
                if exists:
                    raise ConfigurationError("Only draft exchanges can be deleted.")
                raise KeyError(exchange_id)
