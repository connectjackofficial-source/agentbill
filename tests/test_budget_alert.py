"""Tests for agentbill budget_alert."""
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agentbill.bill import Ledger


def _ledger():
    tmp = tempfile.TemporaryDirectory()
    l = Ledger(Path(tmp.name) / "bill.db")
    return l, tmp


def test_over_and_warn_levels():
    l, tmp = _ledger()
    l.set_budget("tokens", 100.0)
    l.set_budget("follower", 50.0)
    # spend 120 on tokens (over), 45 on follower (90% = warn)
    month = time.strftime("%Y-%m")
    l.conn.execute(
        "INSERT INTO entries (tool, model, tokens_in, tokens_out, cost, ts) "
        "VALUES ('tokens','claude',10,10,?,?)", (120.0, month + "-01 00:00:00"))
    l.conn.execute(
        "INSERT INTO entries (tool, model, tokens_in, tokens_out, cost, ts) "
        "VALUES ('follower','claude',10,10,?,?)", (45.0, month + "-01 00:00:00"))
    l.conn.commit()
    alerts = {a["tool"]: a for a in l.budget_alert()}
    assert alerts["tokens"]["level"] == "over"
    assert alerts["follower"]["level"] == "warn"
    assert alerts["tokens"]["usage"] > 1.0
    l.close()
    tmp.cleanup()
    print("test_over_and_warn_levels: ok")


def test_no_alerts_under_warn_threshold():
    l, tmp = _ledger()
    l.set_budget("tokens", 100.0)
    l.add("tokens", "claude", 10, 10)  # tiny real cost, far below
    assert l.budget_alert() == []
    l.close()
    tmp.cleanup()
    print("test_no_alerts_under_warn_threshold: ok")


def test_custom_warn_threshold():
    l, tmp = _ledger()
    l.set_budget("tokens", 100.0)
    # insert a fixed cost row (2% of budget) so a 1% threshold warns
    month = time.strftime("%Y-%m")
    l.conn.execute(
        "INSERT INTO entries (tool, model, tokens_in, tokens_out, cost, ts) "
        "VALUES ('tokens','claude',10,10,?,?)", (2.0, month + "-01 00:00:00"))
    l.conn.commit()
    alerts = l.budget_alert(warn_at=0.01)  # anything above 1% warns
    assert any(a["tool"] == "tokens" and a["level"] == "warn"
               for a in alerts)
    l.close()
    tmp.cleanup()
    print("test_custom_warn_threshold: ok")


if __name__ == "__main__":
    test_over_and_warn_levels()
    test_no_alerts_under_warn_threshold()
    test_custom_warn_threshold()
    print("agentbill budget_alert tests passed")
