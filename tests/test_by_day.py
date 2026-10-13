"""Tests for Ledger.cost_by_day (gap-free daily series)."""
import datetime
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agentbill.bill import Ledger


def test_gap_free_series():
    tmp = tempfile.TemporaryDirectory()
    ledger = Ledger(Path(tmp.name) / "ledger.db")
    today = datetime.date.today()
    # one entry yesterday, one today
    y = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%dT10:00:00")
    t = today.strftime("%Y-%m-%dT10:00:00")
    ledger.add("code", "gpt", 1000, 500, ts=y)
    ledger.add("code", "gpt", 2000, 1000, ts=t)
    series = ledger.cost_by_day(days=7)
    assert len(series) == 7
    assert series[0]["day"] == (today - datetime.timedelta(days=6)).isoformat()
    assert series[-1]["day"] == today.isoformat()
    # gap-free: every day present, empty days cost 0.0
    assert all(0 <= d["cost"] for d in series)
    y_day = (today - datetime.timedelta(days=1)).isoformat()
    entry = next(d for d in series if d["day"] == y_day)
    assert entry["calls"] == 1 and entry["cost"] > 0
    empty = next(d for d in series
                 if d["day"] == (today - datetime.timedelta(days=3)).isoformat())
    assert empty["calls"] == 0 and empty["cost"] == 0.0
    ledger.close()
    tmp.cleanup()
    print("test_gap_free_series: ok")


def test_empty_ledger():
    tmp = tempfile.TemporaryDirectory()
    ledger = Ledger(Path(tmp.name) / "ledger.db")
    series = ledger.cost_by_day(days=3)
    assert len(series) == 3
    assert all(d["cost"] == 0.0 and d["calls"] == 0 for d in series)
    ledger.close()
    tmp.cleanup()
    print("test_empty_ledger: ok")


def test_costs_sum_to_total():
    tmp = tempfile.TemporaryDirectory()
    ledger = Ledger(Path(tmp.name) / "ledger.db")
    today = datetime.date.today()
    ts = today.strftime("%Y-%m-%dT09:00:00")
    ledger.add("code", "claude", 1000, 500, ts=ts)
    ledger.add("search", "gemini", 500, 250, ts=ts)
    series = ledger.cost_by_day(days=1)
    assert len(series) == 1
    assert abs(series[0]["cost"] - ledger.total_cost("today")) < 1e-6
    ledger.close()
    tmp.cleanup()
    print("test_costs_sum_to_total: ok")


if __name__ == "__main__":
    test_gap_free_series()
    test_empty_ledger()
    test_costs_sum_to_total()
    print("agentbill cost_by_day tests passed")
