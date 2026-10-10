"""Tests for usage-by-model aggregation."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agentbill.bill import Ledger


def test_usage_by_model_groups():
    with tempfile.TemporaryDirectory() as d:
        ledger = Ledger(Path(d) / "l.db")
        try:
            today = "2026-10-10T10:00:00"
            ledger.add("cursor", model="claude-sonnet", tokens_in=1000,
                       tokens_out=0, ts=today)
            ledger.add("cursor", model="claude-sonnet", tokens_in=2000,
                       tokens_out=0, ts=today)
            ledger.add("codex", model="gpt-4o", tokens_in=4000,
                       tokens_out=0, ts=today)
            usage = ledger.usage_by_model("today")
            assert set(usage) == {"claude-sonnet", "gpt-4o"}
            assert usage["claude-sonnet"]["calls"] == 2
            assert usage["claude-sonnet"]["tokens_in"] == 3000
            # claude price 0.003/1k: 1000+2000 -> 3k -> $0.009
            assert usage["claude-sonnet"]["cost"] == round(0.009, 6)
            assert usage["gpt-4o"]["cost"] == round(0.01, 6)
        finally:
            ledger.close()
    print("test_usage_by_model_groups: ok")


def test_usage_by_model_empty():
    with tempfile.TemporaryDirectory() as d:
        ledger = Ledger(Path(d) / "l.db")
        try:
            assert ledger.usage_by_model() == {}
        finally:
            ledger.close()
    print("test_usage_by_model_empty: ok")


if __name__ == "__main__":
    test_usage_by_model_groups()
    test_usage_by_model_empty()
    print("agentbill usage-by-model tests passed")
