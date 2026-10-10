# agentbill

> Track token usage and dollar cost across Claude Code, Cursor, Codex, and other AI
> coding agents. Zero-config, terminal-first.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

AI coding tools bill by the token. You switch between Claude Code, Cursor, and
Codex during a week and have no idea what it actually costs you. `agentbill`
reads the local usage logs these tools already write and prints one terminal
table: how many tokens, how many dollars, per tool, today.

## Install

```bash
git clone https://github.com/connectjackofficial-source/agentbill.git
cd agentbill
python -m pip install -r requirements.txt
```

## Usage

```bash
# record a call (from your own scripts or the log parsers)
python -m agentbill add claude-code --model claude-sonnet --tokens-in 1000 --tokens-out 500

# report per tool (today / week / all)
python -m agentbill report today
python -m agentbill report week

# export everything to CSV for a spreadsheet
python -m agentbill export --out ledger.csv

# cap monthly spend per tool
python -m agentbill budget set claude-code --limit 20
python -m agentbill budget status
# {"claude-code": {"spent": 3.2, "limit": 20.0, "remaining": 16.8, "over": false}}
```

## How it works

A local SQLite ledger (`~/.agentbill/ledger.db`) stores every call. Costs are
estimated from per-model-family prices (input/output per 1k tokens) with zero
configuration. Log parsers for Claude Code / Cursor / Codex feed into the
same ledger.

## FAQ

**Why not just check the provider dashboard?** Because you use three providers.
This gives you one table.

**Are the prices exact?** They are approximate model-family rates. Pass exact
costs if you need invoice-grade numbers.

## License

MIT
