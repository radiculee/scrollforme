from pathlib import Path

from scrollforme.config import BrowserSettings
from scrollforme.browser import build_login_command


def test_login_uses_the_profile_and_nodriver_password_store():
	browser = BrowserSettings(profile_dir=Path("/tmp/profile"))
	command = build_login_command(browser, ["https://www.reddit.com"])
	assert command[0] == "google-chrome"
	assert f"--user-data-dir={browser.profile_dir}" in command
	assert "--password-store=basic" in command
	assert command[-1] == "https://www.reddit.com"
