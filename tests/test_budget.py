"""Tests for the agentbill budget feature."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agentbill.bill import Ledger


def test_budget_status_ok():
    with tempfile.TemporaryDirectory() as d:
        ledger = Ledger(Path(d) / "l.db")
        ledger.set_budget("claude-code", 10.0)
        ledger.add("claude-code", "claude-sonnet", 1000, 500)  # ~0.0105
        status = ledger.budget_status()
        assert "claude-code" in status
        assert status["claude-code"]["limit"] == 10.0
        assert status["claude-code"]["spent"] > 0
        assert status["claude-code"]["over"] is False
        assert status["claude-code"]["remaining"] < 10.0
        ledger.close()
    print("test_budget_status_ok: ok")


def test_budget_over_flag():
    with tempfile.TemporaryDirectory() as d:
        ledger = Ledger(Path(d) / "l.db")
        # 1 cent budget
        over = ledger.set_budget("cursor", 0.001)
        ledger.add("cursor", "gpt-4o", 10000, 5000)  # ~0.075
        status = ledger.budget_status()
        assert status["cursor"]["over"] is True
        assert status["cursor"]["remaining"] < 0
        ledger.close()
    print("test_budget_over_flag: ok")


if __name__ == "__main__":
    test_budget_status_ok()
    test_budget_over_flag()
    print("agentbill budget tests passed")
