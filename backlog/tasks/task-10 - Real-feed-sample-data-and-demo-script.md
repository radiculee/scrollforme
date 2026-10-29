---
id: TASK-10
title: Real feed sample data and demo script
status: To Do
assignee: []
created_date: '2026-10-29 20:05'
labels:
  - hackathon
dependencies: []
priority: high
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
P2, branch `sample-data`. Owns `src/scrollforme/reddit_json.py`, `samples/` and the demo script.

1. In a normal browser logged in to Reddit, save `https://old.reddit.com/.json?limit=25` as `feed.json` (outside the repo, or in the git-ignored `output/`).
2. `uv run --frozen scrollforme import-reddit feed.json` and send the resulting `digest.json` to P3 and P4 in chat. Do not commit it: it is someone's personal feed.
3. Write a 3-minute demo script and take backup screenshots of the finished page.
4. If time is left, fix whatever the real data shows `reddit_json.py` gets wrong.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 P3 and P4 have a real digest.json within 10 minutes
- [ ] #2 A demo script and backup screenshots exist
<!-- AC:END -->
