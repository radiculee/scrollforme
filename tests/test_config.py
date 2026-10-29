import tomllib
from pathlib import Path

import pytest

from scrollforme import config
from scrollforme.config import get_settings, load_settings, parse_settings, use_settings

REPO_ROOT = Path(__file__).parent.parent
EXAMPLE_CONFIG = REPO_ROOT / "scrollforme.example.toml"


def test_example_config_loads():
	settings = load_settings(EXAMPLE_CONFIG)
	assert [source.module for source in settings.sources] == ["reddit.com"]
	assert settings.modules_dir == REPO_ROOT / "modules"
	assert settings.browser.profile_dir.is_absolute()
	assert "~" not in settings.mcp.command
	assert all("~" not in arg for arg in settings.mcp.args)


def test_relative_paths_resolve_against_config_dir(tmp_path):
	raw = {"sources": [{"module": "a.com", "description": "news"}]}
	settings = parse_settings(raw, base_dir=tmp_path)
	assert settings.browser.profile_dir == tmp_path / "profile"
	assert settings.output_dir == tmp_path / "output"
	assert settings.modules_dir == tmp_path / "modules"


def test_config_without_sources_is_rejected(tmp_path):
	with pytest.raises(ValueError, match="no \\[\\[sources\\]\\]"):
		parse_settings({}, base_dir=tmp_path)


def test_blank_description_is_rejected(tmp_path):
	raw = {"sources": [{"module": "a.com", "description": "  "}]}
	with pytest.raises(ValueError, match="without a description"):
		parse_settings(raw, base_dir=tmp_path)


def test_unknown_source_key_is_rejected(tmp_path):
	raw = tomllib.loads('[[sources]]\nmodule = "a.com"\ndescription = "x"\nurl = "https://x"\n')
	with pytest.raises(TypeError):
		parse_settings(raw, base_dir=tmp_path)


def test_get_settings_returns_what_use_settings_set(monkeypatch):
	monkeypatch.setattr(config, "_active_settings", None)
	settings = load_settings(EXAMPLE_CONFIG)
	use_settings(settings)
	assert get_settings() is settings
