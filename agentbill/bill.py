"""agentbill ledger: record token usage and dollar cost per tool.

Storage is a single SQLite file (zero setup). Rows are keyed by
(tool, ts, model, tokens_in, tokens_out) with a computed cost.
"""
from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

# Approximate $ per 1k tokens (input, output) by model family.
PRICES = {
    "claude": (0.003, 0.015),
    "gpt": (0.0025, 0.01),
    "gemini": (0.00125, 0.005),
    "other": (0.002, 0.008),
}


def db_path() -> Path:
    root = os.environ.get("AGENTBILL_DIR")
    if root:
        return Path(root) / "ledger.db"
    return Path.home() / ".agentbill" / "ledger.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    tool TEXT NOT NULL,
    model TEXT,
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    cost REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS budgets (
    tool TEXT PRIMARY KEY,
    monthly_limit REAL NOT NULL
);
"""


def _price_family(model: str) -> str:
    m = (model or "").lower()
    for key in ("claude", "gpt", "gemini"):
        if key in m:
            return key
    return "other"


def _cost(model: str, tokens_in: int, tokens_out: int) -> float:
    in_rate, out_rate = PRICES[_price_family(model)]
    return (tokens_in / 1000) * in_rate + (tokens_out / 1000) * out_rate


class Ledger:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)

    def add(self, tool: str, model: str = "other",
            tokens_in: int = 0, tokens_out: int = 0,
            ts: Optional[str] = None) -> int:
        ts = ts or time.strftime("%Y-%m-%dT%H:%M:%S")
        cost = _cost(model, tokens_in, tokens_out)
        cur = self.conn.execute(
            "INSERT INTO entries (ts, tool, model, tokens_in, tokens_out, cost) "
            "VALUES (?,?,?,?,?,?)",
            (ts, tool, model, tokens_in, tokens_out, round(cost, 6)))
        self.conn.commit()
        return cur.lastrowid

    def summary(self, period: str = "today") -> dict:
        """Aggregate by tool for a period: today | week | all."""
        if period == "today":
            day = time.strftime("%Y-%m-%d")
            where = "WHERE ts LIKE ?"
            arg = (day + "%",)
        elif period == "week":
            where = "WHERE ts >= datetime('now', '-7 days')"
            arg = ()
        else:
            where = ""
            arg = ()
        rows = self.conn.execute(
            f"SELECT tool, COUNT(*), SUM(tokens_in), SUM(tokens_out), "
            f"SUM(cost) FROM entries {where} GROUP BY tool ORDER BY SUM(cost) DESC",
            arg).fetchall()
        return {r[0]: {"calls": r[1], "tokens_in": r[2], "tokens_out": r[3],
                       "cost": round(r[4] or 0, 6)} for r in rows}

    def total_cost(self, period: str = "today") -> float:
        return round(sum(v["cost"] for v in self.summary(period).values()), 6)

    def usage_by_model(self, period: str = "today") -> dict:
        """Aggregate cost by model family for a period: today | week | all."""
        if period == "today":
            day = time.strftime("%Y-%m-%d")
            where = "WHERE ts LIKE ?"
            arg = (day + "%",)
        elif period == "week":
            where = "WHERE ts >= datetime('now', '-7 days')"
            arg = ()
        else:
            where = ""
            arg = ()
        rows = self.conn.execute(
            f"SELECT model, COUNT(*), SUM(tokens_in), SUM(tokens_out), "
            f"SUM(cost) FROM entries {where} "
            f"GROUP BY model ORDER BY SUM(cost) DESC", arg).fetchall()
        return {r[0] or "other": {"calls": r[1], "tokens_in": r[2],
                                  "tokens_out": r[3],
                                  "cost": round(r[4] or 0, 6)} for r in rows}

    def export_csv(self, path: Optional[Path] = None) -> Path:
        """Write all entries to CSV. Returns the output path."""
        import csv
        out = Path(path) if path else self.path.with_name("ledger.csv")
        rows = self.conn.execute(
            "SELECT id, ts, tool, model, tokens_in, tokens_out, cost "
            "FROM entries ORDER BY ts").fetchall()
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "ts", "tool", "model",
                             "tokens_in", "tokens_out", "cost"])
            writer.writerows(rows)
        return out

    def close(self):
        self.conn.close()

    def set_budget(self, tool: str, monthly_limit: float) -> bool:
        """Set a monthly $ budget cap for a tool. Returns True if it was
        already over budget."""
        self.conn.execute(
            "INSERT OR REPLACE INTO budgets (tool, monthly_limit) VALUES (?,?)",
            (tool, monthly_limit))
        self.conn.commit()
        return self.budget_status().get(tool, {}).get("over", False)

    def budget_status(self) -> dict:
        """Per-tool spending vs budget for the current calendar month."""
        month = time.strftime("%Y-%m")
        spent = {}
        for row in self.conn.execute(
                "SELECT tool, SUM(cost) FROM entries "
                "WHERE ts LIKE ? GROUP BY tool", (month + "%",)):
            spent[row[0]] = round(row[1] or 0, 6)
        out = {}
        for tool, limit in self.conn.execute("SELECT tool, monthly_limit FROM budgets"):
            used = spent.get(tool, 0.0)
            out[tool] = {
                "spent": used,
                "limit": limit,
                "remaining": round(limit - used, 6),
                "over": used > limit,
            }
        return out
