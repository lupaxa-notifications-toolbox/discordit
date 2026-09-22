"""CLI entrypoint."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lupaxa.discordit.cli import build_parser, main
from lupaxa.discordit.version import get_version

WEBHOOK = "https://discord.com/api/webhooks/123456789012345678/tokenvalue"
_BASE = ["--webhook", WEBHOOK]


def test_help_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--help"]) == 0
    assert "--webhook" in capsys.readouterr().out


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--version"]) == 0
    assert get_version() in capsys.readouterr().out


def test_missing_webhook_exits_two(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--text", "hi"]) == 2
    assert "webhook URL required" in capsys.readouterr().err


def test_missing_mode_exits_two() -> None:
    assert main(_BASE) == 2


def test_validate_with_text_exits_two() -> None:
    assert main([*_BASE, "--validate", "--text", "hi"]) == 2


def test_parser_defaults() -> None:
    args = build_parser().parse_args([*_BASE, "--text", "hi"])
    assert args.webhook == WEBHOOK
    assert args.text == "hi"
    assert args.tts_flag is None
    assert args.timeout is None


def test_timeout_must_be_a_number() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_BASE, "--text", "hi", "--timeout", "nope"])


def test_text_calls_send_payload() -> None:
    client = MagicMock()
    with patch("lupaxa.discordit.cli.Discordit", return_value=client) as ctor:
        assert main([*_BASE, "--username", "PyBot", "--text", "hi"]) == 0
    ctor.assert_called_once_with(
        WEBHOOK,
        username="PyBot",
        avatar_url=None,
        tts=False,
        thread_name=None,
        allowed_mentions=None,
        timeout=10.0,
    )
    client.send_payload.assert_called_once_with({"content": "hi"}, file_path=None)


def test_embed_and_file(tmp_path: Path) -> None:
    path = tmp_path / "report.txt"
    path.write_text("x", encoding="utf-8")
    client = MagicMock()
    client.convert_to_json.return_value = {"title": "Hi"}
    with patch("lupaxa.discordit.cli.Discordit", return_value=client):
        assert (
            main([*_BASE, "--embed", '{"title": "Hi"}', "--file", str(path), "--text", "see"]) == 0
        )
    client.send_payload.assert_called_once_with(
        {"content": "see", "embeds": [{"title": "Hi"}]},
        file_path=str(path),
    )


def test_profile_fills_client_and_flags_override(tmp_path: Path) -> None:
    path = tmp_path / "discordit.yml"
    path.write_text(
        "\n".join(
            [
                "profiles:",
                "  testing:",
                f"    webhook_url: {WEBHOOK}",
                "    username: PyBot",
                "    avatar_url: https://example.com/a.png",
                "    tts: true",
                "    thread_name: Alerts",
                "    timeout: 15",
            ],
        ),
        encoding="utf-8",
    )
    client = MagicMock()
    with patch("lupaxa.discordit.cli.Discordit", return_value=client) as ctor:
        assert main(["-p", "testing", "--config", str(path), "--no-tts", "--text", "hi"]) == 0
    ctor.assert_called_once_with(
        WEBHOOK,
        username="PyBot",
        avatar_url="https://example.com/a.png",
        tts=False,
        thread_name="Alerts",
        allowed_mentions=None,
        timeout=15.0,
    )


def test_unknown_profile_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "discordit.yml"
    path.write_text(
        f"profiles:\n  testing:\n    webhook_url: {WEBHOOK}\n",
        encoding="utf-8",
    )
    assert main(["-p", "missing", "--config", str(path), "--text", "hi"]) == 2
    assert "profile not found" in capsys.readouterr().err


def test_validate_success_and_failure() -> None:
    client = MagicMock()
    client.validate.return_value = True
    with patch("lupaxa.discordit.cli.Discordit", return_value=client):
        assert main([*_BASE, "--validate"]) == 0
    client.validate.return_value = False
    with patch("lupaxa.discordit.cli.Discordit", return_value=client):
        assert main([*_BASE, "--validate"]) == 1


def test_request_error_exits_one(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("lupaxa.discordit.cli.Discordit", side_effect=ValueError("nope")):
        assert main([*_BASE, "--text", "hi"]) == 1
    assert "nope" in capsys.readouterr().err
