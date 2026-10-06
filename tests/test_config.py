"""Tests for agentbill config."""
import json
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_load_config_default():
    from agentbill.config import load_config
    with tempfile.TemporaryDirectory() as d:
        cfg = load_config(Path(d) / "nope.json")
        assert isinstance(cfg, dict)
    print("test_load_config_default: ok")


if __name__ == "__main__":
    test_load_config_default()
    print("agentbill tests passed")
