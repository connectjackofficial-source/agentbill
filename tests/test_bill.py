"""Tests for the agentbill ledger."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agentbill.bill import Ledger, _cost


def test_cost():
    assert _cost("claude-sonnet", 1000, 1000) == 0.003 + 0.015
    assert _cost("gpt-4o", 1000, 1000) == 0.0025 + 0.01
    print("test_cost: ok")


def test_add_and_summary():
    with tempfile.TemporaryDirectory() as d:
        ledger = Ledger(Path(d) / "l.db")
        ledger.add("claude-code", "claude-sonnet", 1000, 500)
        ledger.add("cursor", "gpt-4o", 2000, 800)
        ledger.add("claude-code", "claude-haiku", 100, 50)
        s = ledger.summary(period="all")
        assert s["claude-code"]["calls"] == 2
        assert s["cursor"]["calls"] == 1
        assert s["claude-code"]["cost"] > 0
        assert ledger.total_cost(period="all") > 0
        ledger.close()
    print("test_add_and_summary: ok")


def test_export_csv():
    with tempfile.TemporaryDirectory() as d:
        ledger = Ledger(Path(d) / "l.db")
        ledger.add("codex", "gpt-4o", 500, 200)
        out = ledger.export_csv(Path(d) / "out.csv")
        lines = out.read_text(encoding="utf-8").splitlines()
        assert lines[0].startswith("id,ts,tool")
        assert len(lines) == 2
        ledger.close()
    print("test_export_csv: ok")


if __name__ == "__main__":
    test_cost()
    test_add_and_summary()
    test_export_csv()
    print("agentbill ledger tests passed")
