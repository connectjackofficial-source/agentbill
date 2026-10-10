"""agentbill CLI: record token usage and report cost per tool."""
import argparse
import json

from .bill import Ledger


def main():
    ap = argparse.ArgumentParser(prog="agentbill")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="record a call")
    a.add_argument("tool", choices=["claude-code", "cursor", "codex"])
    a.add_argument("--model", default="other")
    a.add_argument("--tokens-in", type=int, default=0)
    a.add_argument("--tokens-out", type=int, default=0)

    r = sub.add_parser("report", help="aggregate by tool")
    r.add_argument("period", nargs="?", default="today",
                   choices=["today", "week", "all"])

    e = sub.add_parser("export", help="write entries to CSV")
    e.add_argument("--out", default=None)

    b = sub.add_parser("budget", help="set or check monthly budgets")
    bsub = b.add_subparsers(dest="bcmd", required=True)
    bs = bsub.add_parser("set", help="set a budget cap")
    bs.add_argument("tool", choices=["claude-code", "cursor", "codex"])
    bs.add_argument("--limit", type=float, required=True, help="monthly $ cap")
    bsub.add_parser("status", help="show spending vs budget")

    args = ap.parse_args()
    ledger = Ledger()

    if args.cmd == "add":
        rid = ledger.add(args.tool, args.model,
                         args.tokens_in, args.tokens_out)
        print(json.dumps({"recorded": True, "id": rid}))
    elif args.cmd == "report":
        print(json.dumps(ledger.summary(period=args.period), indent=2))
        print(f"total: ${ledger.total_cost(period=args.period)}")
    elif args.cmd == "export":
        out = ledger.export_csv(args.out)
        print(json.dumps({"exported": str(out)}))
    elif args.cmd == "budget":
        if args.bcmd == "set":
            over = ledger.set_budget(args.tool, args.limit)
            print(json.dumps({"budget": args.tool, "limit": args.limit,
                              "already_over": over}))
        elif args.bcmd == "status":
            print(json.dumps(ledger.budget_status(), indent=2))
    ledger.close()


if __name__ == "__main__":
    main()
