---
id: TASK-11
title: Magazine layout
status: To Do
assignee: []
created_date: '2026-10-29 20:05'
labels:
  - hackathon
dependencies: []
priority: high
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
P3, branch `magazine-layout`. Owns `templates/digest.html.j2` except the CSP `<meta>` line and the `<script>` line (TASK-12), plus layout tests in `tests/test_render.py`.

- Results are free-form dicts rendered by the generic `show()` macro. Add a magazine branch for results whose data has a `posts` list (reddit.com returns `{"posts": [...]}` with title, url, subreddit, author, posted_at, summary, text); keep `show()` for everything else.
- Masthead with the date, the first post as the lead story, then one section per subreddit (Jinja `groupby('subreddit')`), each post with a `text` excerpt (`|truncate(300)`).
- Keep the CSS inline in `<style>`: the CSP allows only inline styles.
- Every post stays wrapped in `<article class="post" data-url="...">` with an http(s) URL only (use the `link` test); the save and notes script finds posts by it.
- Never use `|safe` on site data. Keep the "That's everything" footer.
- Preview: `uv run --frozen scrollforme render output/<run>/digest.json`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Posts are grouped into one section per subreddit under a lead story
- [ ] #2 test_site_text_is_escaped_at_any_depth and test_only_http_urls_become_links still pass
<!-- AC:END -->
