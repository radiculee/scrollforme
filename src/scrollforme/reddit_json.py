"""Turn a saved Reddit listing (old.reddit.com/.json) into a reddit.com result.

This is the offline path for sample data and a demo fallback: open
old.reddit.com/.json while logged in, save it, and import it. The output has the
same `{"posts": [...]}` shape the reddit.com module asks the agent for, so the
page renders both alike. The listing is written by strangers and is capped
here, then rendered as escaped text like any module's output.
"""

import re
import html
from datetime import UTC, datetime

IMPORT_DESCRIPTION = "My home feed, imported from a saved old.reddit.com/.json."
REDDIT_BASE_URL = "https://www.reddit.com"
SUMMARY_MAX_CHARS = 200
TEXT_MAX_CHARS = 1000


def posts_from_listing(listing: dict, max_items: int) -> dict:
	"""Map the listing's posts to `{"posts": [...]}`, skipping promoted and stickied ones."""
	posts = [child["data"] for child in listing["data"]["children"] if child.get("kind") == "t3"]
	shown = [post for post in posts if not post.get("promoted") and not post.get("stickied")]
	return {"posts": [_post(post) for post in shown[:max_items]]}


def _post(post: dict) -> dict:
	# Reddit's JSON HTML-escapes titles and text; the template escapes them again.
	text = html.unescape(post.get("selftext", "")).strip()
	return {
		"title": html.unescape(post.get("title", "")),
		"url": REDDIT_BASE_URL + post.get("permalink", ""),
		"subreddit": post.get("subreddit_name_prefixed", ""),
		"author": post.get("author", ""),
		"posted_at": _format_time(post.get("created_utc")),
		"summary": _summary(post, text),
		"text": text[:TEXT_MAX_CHARS],
	}


def _summary(post: dict, text: str) -> str:
	if text:
		first_line = text.split("\n", 1)[0]
		return re.split(r"(?<=[.!?])\s", first_line, maxsplit=1)[0][:SUMMARY_MAX_CHARS]
	if post.get("is_self"):
		return ""
	return f"Link to {post.get('domain', 'another site')}."


def _format_time(created_utc: float | None) -> str:
	if created_utc is None:
		return ""
	return datetime.fromtimestamp(created_utc, UTC).strftime("%Y-%m-%d %H:%M UTC")
