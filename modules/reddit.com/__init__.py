"""reddit.com: the user's subreddits and home feed, without the endless scroll."""

from scrollforme.agent import browse_site

__all__ = ["browse"]

# old.reddit lists 25 posts per page with no infinite scroll, so one page is the whole visit.
_START_URL = "https://old.reddit.com/"

_GUIDANCE = """\
Read the logged-in home feed (the user's subscribed subreddits) in the order shown and take at
most the first 25 posts; do not page further. Skip promoted and stickied posts. Return
{"posts": [...]} where each post has title, url (its comments permalink), subreddit (r/name),
author, posted_at, a one-line summary, and text (the post's own words if the page shows them).
Leave out vote and comment counts. Read comments only if the description asks for them."""


def browse(description: str) -> dict:
	"""Visit Reddit for the purpose in `description` and return what was found."""
	return browse_site("reddit.com", _START_URL, description, _GUIDANCE)
