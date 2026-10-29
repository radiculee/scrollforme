---
id: TASK-9
title: Live Reddit run on Windows
status: To Do
assignee: []
created_date: '2026-10-29 20:05'
labels:
  - hackathon
  - mvp
dependencies:
  - TASK-1
priority: high
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
P1, branch `scraper-windows`. Owns `agent.py`, `config.py`, `browser.py`, `modules/reddit.com/` and the local `scrollforme.toml`.

1. Clone stealth-browser-mcp to `~/.local/src/stealth-browser-mcp`, create its venv and install its requirements.
2. Copy `scrollforme.example.toml` to `scrollforme.toml`: `chrome_binary = "C:/Program Files/Google/Chrome/Application/chrome.exe"`, `[mcp] command` = `.venv/Scripts/python.exe` in the checkout.
3. `uv run --frozen scrollforme login`, log in to Reddit, close Chrome.
4. `uv run --frozen scrollforme run`. The reddit.com module reads old.reddit.com's home feed and must return `{"posts": [...]}` (see its guidance); layout and notes depend on that shape.

Time box: if it isn't working 20 minutes before the demo, the demo uses `import-reddit` data (TASK-10).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A live run writes a digest.html with real home-feed posts in the {"posts": [...]} shape
- [ ] #2 Observed cost and turns are noted (also covers TASK-1)
- [ ] #3 The safety invariants in AGENTS.md are unchanged and tests/test_agent.py passes
<!-- AC:END -->
