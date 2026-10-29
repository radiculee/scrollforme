---
id: TASK-12
title: Save and notes script
status: To Do
assignee: []
created_date: '2026-10-29 20:05'
labels:
  - hackathon
  - safety
dependencies: []
priority: high
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
P4, branch `save-notes`. Owns the new `templates/workspace.js`, `render.py`, the template's CSP `<meta>` line and one `<script>` line just before `</body>`, plus script tests in `tests/test_render.py`.

- `render.py` loads `workspace.js`, computes its base64 sha256, and passes both to the template.
- CSP: `default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-<hash>'`.
- `<script>{{ workspace_js | safe }}</script>`: our own static file, never site data.
- For each `article.post`, add a star button and a note textarea with `createElement`. Store `{saved, note}` in localStorage under `scrollforme:<data-url>`. A "Saved only" toggle hides unsaved posts. No `innerHTML`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Stars and notes survive a page reload in Chrome
- [ ] #2 A test checks the CSP hash matches the script and script-src has no 'unsafe-inline'
- [ ] #3 test_site_text_is_escaped_at_any_depth still passes
<!-- AC:END -->
