import json
from pathlib import Path

from scrollforme.reddit_json import TEXT_MAX_CHARS, posts_from_listing

LISTING = json.loads((Path(__file__).parent / "fixtures/reddit_listing.json").read_text("utf-8"))


def _posts(max_items=25):
	return posts_from_listing(LISTING, max_items)["posts"]


def test_promoted_and_stickied_posts_are_skipped():
	assert [post["author"] for post in _posts()] == ["gpu_tinkerer", "pedal_pusher", "page_turner"]


def test_post_fields_are_mapped_and_unescaped():
	post = _posts()[0]
	assert post["title"] == "Running a 70B model on two used GPUs & what I learned"
	assert post["url"] == "https://www.reddit.com/r/LocalLLaMA/comments/aaa002/running_a_70b_model/"
	assert post["subreddit"] == "r/LocalLLaMA"
	assert post["summary"] == "I split the layers across both cards."
	assert post["text"].endswith("Details below.")
	assert post["posted_at"] == "2026-10-29 09:00 UTC"


def test_link_posts_are_summarised_by_domain():
	assert _posts()[1]["summary"] == "Link to citynews.example.com."


def test_import_is_capped_in_count_and_text_length():
	listing = {"data": {"children": [{"kind": "t3", "data": {"selftext": "x" * 5000}}] * 3}}
	posts = posts_from_listing(listing, max_items=2)["posts"]
	assert len(posts) == 2
	assert len(posts[0]["text"]) == TEXT_MAX_CHARS
