"""Minimal CLI: prints what agentbill will report once log sources are wired."""
import argparse


def main():
    ap = argparse.ArgumentParser(prog="agentbill")
    ap.add_argument("period", nargs="?", default="today",
                    choices=["today", "week"])
    ap.add_argument("--tool", default=None)
    args = ap.parse_args()
    tool = args.tool or "all"
    print(f"agentbill v0.1.0")
    print(f"period={args.period}  tool={tool}")
    print("log sources: claude-code, cursor, codex")
    print("(parsers wiring in progress)")


if __name__ == "__main__":
    main()
