from datetime import datetime

from scrollforme.models import SourceResult
from scrollforme.render import render_digest, split_headline

GENERATED_AT = datetime(2026, 10, 29, 8, 30)


def _render(data: dict) -> str:
	return render_digest([SourceResult("reddit.com", "news", data=data)], GENERATED_AT)


def test_site_text_is_escaped_at_any_depth():
	html = _render({"posts": [{"title": "<script>alert(1)</script>", "notes": {"x": "<b>hi</b>"}}]})
	assert "<script>alert" not in html
	assert "&lt;script&gt;" in html
	assert "<b>hi</b>" not in html


def test_only_http_urls_become_links():
	html = _render({"a": "https://example.com/x", "b": "javascript:alert(1)"})
	assert 'href="https://example.com/x"' in html
	assert 'href="javascript' not in html


def test_entry_with_title_and_url_becomes_headline():
	html = _render({"posts": [{"title": "New model", "url": "https://r.com/p", "score": 5}]})
	assert (
		'<p class="headline"><a href="https://r.com/p" rel="noreferrer">New model</a></p>' in html
	)
	assert "<dt>score</dt>" in html


def test_headline_entries_are_posts_keyed_by_url():
	html = _render({"posts": [{"title": "New model", "url": "https://r.com/p", "score": 5}]})
	assert '<article class="post" data-url="https://r.com/p">' in html
	assert html.index("<dt>score</dt>") < html.index("</article>")


def test_split_headline_leaves_entries_without_a_link_alone():
	entry = {"title": "T", "url": "ftp://x"}
	assert split_headline(entry) == ("", "", entry)


def test_page_shows_purpose_and_failed_sites():
	ok = SourceResult("reddit.com", "I follow r/LocalLLaMA", data={"summary": "quiet day"})
	failed = SourceResult("instagram.com", "friends", error="timed out")
	html = render_digest([ok, failed], GENERATED_AT)
	assert "2 sites" in html
	assert "I follow r/LocalLLaMA" in html
	assert "Could not read this site: timed out" in html
