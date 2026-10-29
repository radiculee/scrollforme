from pathlib import Path

from scrollforme.config import load_settings
from scrollforme.agent import (
	READ_ONLY_BROWSER_TOOLS,
	WRITING_BROWSER_TOOLS,
	SiteTask,
	decode_nested_json,
	build_options,
	build_prompt,
)

SETTINGS = load_settings(Path(__file__).parent.parent / "scrollforme.example.toml")


def test_agent_has_no_builtin_tools_and_denies_unlisted_calls():
	options = build_options(SETTINGS)
	assert options.tools == []
	assert options.permission_mode == "dontAsk"
	assert options.setting_sources == []


def test_no_mcp_server_but_the_browser_can_load():
	options = build_options(SETTINGS)
	assert list(options.mcp_servers) == ["browser"]
	assert options.strict_mcp_config is True
	assert options.env["ENABLE_CLAUDEAI_MCP_SERVERS"] == "false"


def test_only_read_only_browser_tools_are_allowed():
	options = build_options(SETTINGS)
	assert options.allowed_tools == [f"mcp__browser__{name}" for name in READ_ONLY_BROWSER_TOOLS]
	assert options.disallowed_tools == [f"mcp__browser__{name}" for name in WRITING_BROWSER_TOOLS]
	assert set(WRITING_BROWSER_TOOLS).isdisjoint(READ_ONLY_BROWSER_TOOLS)


def test_server_starts_with_unused_sections_disabled():
	args = build_options(SETTINGS).mcp_servers["browser"]["args"]
	assert "--disable-network-debugging" in args
	assert "--disable-browser-management" not in args
	assert "--disable-element-interaction" not in args


def test_prompt_carries_profile_site_and_purpose():
	task = SiteTask("reddit.com", "https://www.reddit.com/", "new open models", "skip promos")
	prompt = build_prompt(task, SETTINGS)
	assert repr(SETTINGS.browser.profile_dir.as_posix()) in prompt
	assert "stay on reddit.com" in prompt
	assert "new open models" in prompt
	assert "skip promos" in prompt


def test_output_is_any_json_object():
	assert build_options(SETTINGS).output_format["schema"]["type"] == "object"


def test_json_encoded_nested_values_are_decoded():
	raw = {"status": "ok", "posts": '[{"title": "x", "tags": "[\\"a\\"]"}]', "note": "[draft] text"}
	assert decode_nested_json(raw) == {
		"status": "ok",
		"posts": [{"title": "x", "tags": ["a"]}],
		"note": "[draft] text",
	}
