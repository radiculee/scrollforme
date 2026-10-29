# scrollforme: agent notes

Read `README.md` first for what the tool does and how a run flows.

## Project facts

- Python 3.12 managed with `uv`. Code is indented with tabs (enforced by `ruff format`). Imports go in groups (standard library, third party, local), and each group is sorted by line length, not alphabetically, which is why ruff's `I` rule is off.
- `modules/<domain>/` holds one Python package per website, and each exports only `browse(description: str) -> dict`. The dotted folder names can't be imported normally; `site_modules.load_browse` loads them from their files. The shipped modules are stubs that call `agent.browse_site`.
- `src/scrollforme/`:
  - `config`: TOML → settings, plus `use_settings`/`get_settings`, because `browse()` takes no settings argument.
  - `site_modules`: the module loader.
  - `agent`: Agent SDK options, prompt and `browse_site`.
  - `models`: the per-source result record.
  - `browser`: manual login.
  - `render` + `templates/`: generic HTML rendering of free-form dicts. Every entry with a title and an http(s) URL is wrapped in `<article class="post" data-url="...">`.
  - `reddit_json`: offline import of a saved old.reddit.com/.json into the same `{"posts": [...]}` shape the reddit.com module asks the agent for.
  - `cli`.
- The agent's output schema is a free-form object. Live runs showed the model sends nested lists as JSON-encoded strings, even with a recursive schema, so `agent.decode_nested_json` decodes them.
- Personal files are git-ignored and must stay out of commits: `scrollforme.toml`, `profile/` (holds real login cookies), `output/`.

## Safety invariants

Do not weaken these without the user's explicit agreement:

1. The browsing agent gets:
   - `tools=[]`, `permission_mode="dontAsk"` and `setting_sources=[]`;
   - only the tools in `agent.READ_ONLY_BROWSER_TOOLS`, with `WRITING_BROWSER_TOOLS` disallowed;
   - `strict_mcp_config=True` and `ENABLE_CLAUDEAI_MCP_SERVERS=false`.

   The last two settings matter: without them the account's claude.ai connectors (Google Drive and others) load into the agent. Adding a tool that can type, click, upload, run scripts or write files gives injected feed content a way to act as the logged-in user. `tests/test_agent.py` pins all of this, and the SDK init message's `tools` list is how to check it live.
2. The agent returns JSON. Only `render.py`, with autoescaping on, turns site content into HTML, and only `http(s)` strings become links. The page may run exactly one script, our own `templates/workspace.js`, allowed by its sha256 in the CSP (no `'unsafe-inline'` for scripts). It builds its controls with `createElement` and `textContent` and never inserts site text as HTML (no `innerHTML`).
3. Every site visit has `max_turns` and `max_budget_usd`.

## Testing

`uv run --frozen pytest` runs offline. A live run needs a logged-in `profile/`, Chrome and an Anthropic credential, so it is a manual check, not a unit test.

## Team workflow (hackathon)

The current target is the Reddit home feed (old.reddit.com, first 25 posts) rendered as a magazine with save and notes. The reddit.com module and `import-reddit` both produce `{"posts": [{title, url, subreddit, author, posted_at, summary, text}]}`, and layout and notes rely on that shape. Each person works on their own branch; the main agent stays on `master` and merges.

| Branch | Worktree folder (main laptop) | Owner | Owns | Task |
|---|---|---|---|---|
| `master` | `scrollforme/` | Main agent | merges, `AGENTS.md`, `README.md` | Merge, test, re-render the demo page |
| `scraper-windows` | `scrollforme-scraper-windows/` | P1 | `agent.py`, `config.py`, `browser.py`, `modules/reddit.com/`, local `scrollforme.toml` | TASK-9 |
| `sample-data` | `scrollforme-sample-data/` | P2 | `reddit_json.py`, `samples/`, demo script | TASK-10 |
| `magazine-layout` | `scrollforme-magazine-layout/` | P3 | `digest.html.j2` except the CSP `<meta>` and `<script>` lines; layout tests in `test_render.py` | TASK-11 |
| `save-notes` | `scrollforme-save-notes/` | P4 | `templates/workspace.js`, `render.py`, the CSP and `<script>` lines of the template; script tests in `test_render.py` | TASK-12 |

- Worktrees exist only on the main laptop. On your own laptop: `git clone https://github.com/radiculee/scrollforme`, `git switch <branch>`, `uv sync --frozen`.
- Always use `uv sync --frozen` and `uv run --frozen`. A newer uv rewrites `uv.lock` otherwise; never commit `uv.lock`.
- Only edit files you own, and keep every post wrapped in `<article class="post" data-url="...">`.
- `uv run --frozen pytest`, `ruff format --check .` and `ruff check .` must pass before you push.
- Push your branch and tell the main agent. Merge order: `sample-data`, `scraper-windows`, `magazine-layout`, `save-notes`. Merges freeze 15 minutes before the demo.

## Tasks

Use the Backlog.md MCP tools (or the `backlog` CLI) for work items in `backlog/`.
