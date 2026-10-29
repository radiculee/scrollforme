# scrollforme

Feeds like Reddit and Instagram are built to keep you scrolling. scrollforme lets an AI agent do the scrolling instead. You say in plain words what you use each site for. The agent visits the site in a browser that is already logged in as you, takes only what serves that purpose, and writes one static HTML page that ends.

Everything runs on your machine. The agent drives Chrome through [stealth-browser-mcp](https://github.com/vibheksoni/stealth-browser-mcp) and runs on the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk).

## How it works

```
scrollforme.toml ─► for each [[sources]] ─► modules/<domain>.browse(description) ─► dict
                                                   │
                                                   ▼  scrollforme.agent.browse_site(...)
                                     Claude agent ─► stealth-browser MCP ─► Chrome (your profile)

dicts ─► output/<timestamp>/digest.json ─► digest.html (Jinja2)
```

- **One module per website.** `modules/reddit.com/`, `modules/instagram.com/` and so on. Each is a Python package exporting one function, `browse(description: str) -> dict`. `description` is your plain-language account of what you use the site for. The returned dict is free-form: whatever the module extracted.
- **One visit per source**, one at a time. Each visit has its own turn and dollar limits, and the agent is told to stop once it has what the description asks for.
- **The agent only reads.** It has no built-in tools (no shell and no file access), and only these browser tools are allowed: spawn, navigate, wait, scroll, query and read the page, and close. Any other call is denied without a prompt. No other MCP server loads, including your Claude Code config and your claude.ai connectors. Feed text is written by strangers and may contain prompt injection, and the browser is logged in as you.
- **The agent returns data, never HTML.** A fixed, autoescaped template renders each dict generically, with a CSP that blocks all scripts. An entry with a `title` and an `http(s)` `url` becomes a headline link, and only `http(s)` strings ever become links.

## Writing a module

Create `modules/<domain>/__init__.py`, export only `browse`, and name the domain in a `[[sources]]` entry. The stubs delegate to the shared agent with a start URL and some site notes:

```python
from scrollforme.agent import browse_site

__all__ = ["browse"]


def browse(description: str) -> dict:
	return browse_site("example.com", "https://example.com/feed", description, "Skip ads.")
```

A module can do anything else it likes instead (an API, RSS, its own parsing) as long as it returns a dict. Folder names contain dots, so `scrollforme.site_modules` loads them from their files, not by `import`. Relative imports inside a module still work.

## Why a separate browser profile

Chrome 136 and later no longer allow remote debugging on your default profile, and Chrome locks any profile that is already open. So scrollforme keeps its own persistent profile in `profile/`. You log in to each site there once and the logins persist.

## Setup

Requirements: [uv](https://docs.astral.sh/uv/), Google Chrome, and a stealth-browser-mcp checkout with its own venv (the default location is `~/.local/src/stealth-browser-mcp`).

```bash
uv sync
cp scrollforme.example.toml scrollforme.toml   # then edit sources and descriptions
uv run scrollforme login                       # opens Chrome on the profile; log in, then close it
uv run scrollforme run                         # writes output/<timestamp>/digest.html
uv run scrollforme render output/<run>/digest.json   # re-render after template changes
uv run scrollforme import-reddit feed.json           # digest from a saved old.reddit.com/.json, no agent
```

**Current target.** The example config reads your Reddit home feed (old.reddit.com, first 25 posts). If the live agent can't run, `import-reddit` builds the same page from `https://old.reddit.com/.json?limit=25` saved from a logged-in browser.

**Windows.** In `scrollforme.toml`, set `chrome_binary = "C:/Program Files/Google/Chrome/Application/chrome.exe"` and point `[mcp] command` at `.venv/Scripts/python.exe` inside the stealth-browser-mcp checkout. Use `uv sync --frozen` and `uv run --frozen`, so a newer uv doesn't rewrite `uv.lock`.

**Authentication.** The Agent SDK uses `ANTHROPIC_API_KEY` if it is set. Otherwise it uses your Claude Code login.

**Cost.** The default model is `claude-opus-5-5` at `medium` effort, capped by `max_budget_usd` per site visit. You can change all three in `[agent]`.

## Development

```bash
uv run pytest
uv run ruff format . && uv run ruff check .
```

Tasks are tracked with [Backlog.md](https://github.com/MrLesk/Backlog.md) in `backlog/`.
