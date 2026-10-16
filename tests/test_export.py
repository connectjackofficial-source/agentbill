"""Tests for agentbill export_csv and top_calls."""
import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agentbill.bill import Ledger


def _ledger():
    tmp = tempfile.TemporaryDirectory()
    return Ledger(Path(tmp.name) / "b.db"), tmp


def test_export_csv_all():
    led, tmp = _ledger()
    led.add("agent", "claude", 1000, 200)
    led.add("agent", "gpt", 500, 100)
    out = Path(tmp.name) / "b.csv"
    returned = led.export_csv(out, period="all")
    assert returned == out
    rows = list(csv.DictReader(out.read_text(encoding="utf-8").splitlines()))
    assert len(rows) == 2
    assert rows[0]["tool"] == "agent"
    assert set(rows[0]) == {"id", "ts", "tool", "model", "tokens_in",
                            "tokens_out", "cost"}
    led.conn.close()
    tmp.cleanup()
    print("test_export_csv_all: ok")


def test_top_calls():
    led, tmp = _ledger()
    led.add("a", "claude", 1000, 200)
    led.add("b", "gpt", 9000, 3000)
    top = led.top_calls(n=1)
    assert top and top[0]["tool"] == "b"
    assert top[0]["cost"] > 0
    led.conn.close()
    tmp.cleanup()
    print("test_top_calls: ok")


if __name__ == "__main__":
    test_export_csv_all()
    test_top_calls()
    print("agentbill export tests passed")
