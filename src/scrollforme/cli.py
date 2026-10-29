"""Command-line entry point: `login`, `run`, `render` and `import-reddit`.

A run writes `<output_dir>/<timestamp>/digest.json` and `digest.html`; `render`
rebuilds the HTML from a saved JSON record without touching the browser, and
`import-reddit` builds a run from a saved old.reddit.com/.json instead.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

from loguru import logger

from scrollforme.render import render_digest
from scrollforme.site_modules import load_browse
from scrollforme.browser import open_profile_for_login
from scrollforme.reddit_json import IMPORT_DESCRIPTION, posts_from_listing
from scrollforme.models import SourceResult, result_from_dict, result_to_dict
from scrollforme.config import DEFAULT_CONFIG_PATH, Settings, Source, load_settings, use_settings


def main() -> None:
	"""Parse arguments and dispatch to a subcommand."""
	args = _build_parser().parse_args()
	args.handler(args)


def _build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="scrollforme", description=__doc__)
	parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
	commands = parser.add_subparsers(required=True)
	commands.add_parser("login", help="open the browser profile to log in").set_defaults(
		handler=_login
	)
	commands.add_parser("run", help="browse every configured site and write a digest").set_defaults(
		handler=_run
	)
	render = commands.add_parser("render", help="rebuild HTML from a saved digest.json")
	render.add_argument("digest_json", type=Path)
	render.set_defaults(handler=_render)
	imports = commands.add_parser(
		"import-reddit", help="build a digest from a saved old.reddit.com/.json"
	)
	imports.add_argument("listing_json", type=Path)
	imports.add_argument("--max-items", type=int, default=25)
	imports.add_argument("--output-dir", type=Path, default=Path("output"))
	imports.set_defaults(handler=_import_reddit)
	return parser


def _login(args: argparse.Namespace) -> None:
	settings = load_settings(args.config)
	urls = [f"https://www.{source.module}/" for source in settings.sources]
	open_profile_for_login(settings.browser, list(dict.fromkeys(urls)))


def _run(args: argparse.Namespace) -> None:
	settings = load_settings(args.config)
	use_settings(settings)
	started_at = datetime.now()
	results = [_browse_or_record_error(source, settings) for source in settings.sources]
	run_dir = settings.output_dir / started_at.strftime("%Y-%m-%d_%H%M%S")
	html_path = _write_run(run_dir, results, started_at)
	logger.info("Digest written to {}", html_path)


def _browse_or_record_error(source: Source, settings: Settings) -> SourceResult:
	"""Run one module; sources go one at a time because they share one locked profile."""
	try:
		data = load_browse(settings.modules_dir, source.module)(source.description)
		return SourceResult(source.module, source.description, data=data)
	except Exception as error:
		logger.exception("Failed to browse {}", source.module)
		return SourceResult(source.module, source.description, error=str(error))


def _write_run(run_dir: Path, results: list[SourceResult], started_at: datetime) -> Path:
	run_dir.mkdir(parents=True, exist_ok=True)
	record = {
		"generated_at": started_at.isoformat(),
		"results": [result_to_dict(result) for result in results],
	}
	record_json = json.dumps(record, indent="\t", ensure_ascii=False)
	(run_dir / "digest.json").write_text(record_json, encoding="utf-8")
	html_path = run_dir / "digest.html"
	html_path.write_text(render_digest(results, started_at), encoding="utf-8")
	return html_path


def _render(args: argparse.Namespace) -> None:
	record = json.loads(args.digest_json.read_text(encoding="utf-8"))
	results = [result_from_dict(data) for data in record["results"]]
	html_path = args.digest_json.with_suffix(".html")
	generated_at = datetime.fromisoformat(record["generated_at"])
	html_path.write_text(render_digest(results, generated_at), encoding="utf-8")
	logger.info("Digest written to {}", html_path)


def _import_reddit(args: argparse.Namespace) -> None:
	listing = json.loads(args.listing_json.read_text(encoding="utf-8"))
	data = posts_from_listing(listing, args.max_items)
	result = SourceResult("reddit.com", IMPORT_DESCRIPTION, data=data)
	started_at = datetime.now()
	run_dir = args.output_dir / started_at.strftime("%Y-%m-%d_%H%M%S")
	logger.info("Digest written to {}", _write_run(run_dir, [result], started_at))
