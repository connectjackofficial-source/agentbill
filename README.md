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
python -m agentbill today      # today's usage per tool
python -m agentbill week       # this week
python -m agentbill --tool claude-code   # one tool only
```

## What it reads

- Claude Code: local session logs
- Cursor: usage JSON
- Codex: CLI usage stats

No API keys, no cloud. Everything is read from your machine.

## License

MIT
