"""Discordit client."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from lupaxa.discordit.client import WEBHOOK_PREFIX, Discordit

WEBHOOK = f"{WEBHOOK_PREFIX}123456789012345678/tokenvalue"


def _response(status: int, text: str = "") -> MagicMock:
    response = MagicMock()
    response.status_code = status
    response.text = text
    return response


def _client(**kwargs: object) -> Discordit:
    with patch("lupaxa.discordit.client.requests.get", return_value=_response(200)):
        return Discordit(WEBHOOK, **kwargs)  # type: ignore[arg-type]


def test_missing_webhook_raises() -> None:
    with pytest.raises(ValueError, match="Webhook URL required"):
        Discordit("")


def test_prefix_is_required() -> None:
    with pytest.raises(ValueError, match="should start with"):
        Discordit("https://example.com/hook")


def test_redirect_on_get_is_rejected() -> None:
    with (
        patch("lupaxa.discordit.client.requests.get", return_value=_response(302)),
        pytest.raises(ValueError, match="please check your configuration") as exc,
    ):
        Discordit(WEBHOOK)
    assert "tokenvalue" not in str(exc.value)


def test_get_error_is_rejected() -> None:
    with (
        patch(
            "lupaxa.discordit.client.requests.get",
            side_effect=requests.ConnectionError("down"),
        ),
        pytest.raises(ValueError, match="please check your configuration"),
    ):
        Discordit(WEBHOOK)


def test_get_401_still_constructs() -> None:
    with patch("lupaxa.discordit.client.requests.get", return_value=_response(401)):
        client = Discordit(WEBHOOK)
    assert client.webhook_url == WEBHOOK


def test_send_message_posts_text_and_omits_defaults() -> None:
    client = _client()
    with patch("lupaxa.discordit.client.requests.post", return_value=_response(204)) as post:
        assert client.send_message("Hello\\nthere") is True
    body = post.call_args.kwargs["json"]
    assert body == {"content": "Hello\nthere"}
    assert post.call_args.kwargs["allow_redirects"] is False


def test_send_message_includes_set_defaults() -> None:
    client = _client(
        username="PyBot",
        avatar_url="https://example.com/a.png",
        tts=True,
        thread_name="Alerts",
        allowed_mentions={"parse": []},
    )
    with patch("lupaxa.discordit.client.requests.post", return_value=_response(204)) as post:
        assert client.send_message("hi") is True
    body = post.call_args.kwargs["json"]
    assert body["username"] == "PyBot"
    assert body["avatar_url"] == "https://example.com/a.png"
    assert body["tts"] is True
    assert body["thread_name"] == "Alerts"
    assert body["allowed_mentions"] == {"parse": []}


def test_send_is_alias() -> None:
    client = _client()
    with patch.object(client, "send_message", return_value=True) as send_message:
        assert client.send("hi") is True
    send_message.assert_called_once_with("hi")


def test_send_embed_wraps_object() -> None:
    client = _client()
    with patch("lupaxa.discordit.client.requests.post", return_value=_response(204)) as post:
        assert client.send_embed('{"title": "Hi"}') is True
    assert post.call_args.kwargs["json"]["embeds"] == [{"title": "Hi"}]


def test_invalid_json_raises() -> None:
    client = _client()
    with pytest.raises(ValueError, match="Invalid json"):
        client.send_embed("not-json")


def test_embed_array_is_rejected() -> None:
    client = _client()
    with pytest.raises(ValueError, match="JSON object"):
        client.send_embed("[]")


def test_send_file_is_multipart(tmp_path: Path) -> None:
    path = tmp_path / "report.txt"
    path.write_bytes(b"data")
    client = _client(tts=True)
    with patch("lupaxa.discordit.client.requests.post", return_value=_response(204)) as post:
        assert client.send_file(str(path), content="see\\nattached") is True
    body = json.loads(post.call_args.kwargs["data"]["payload_json"])
    assert body["content"] == "see\nattached"
    assert body["tts"] is True
    filename, _handle = post.call_args.kwargs["files"]["files[0]"]
    assert filename == "report.txt"


def test_send_file_without_content_omits_content(tmp_path: Path) -> None:
    path = tmp_path / "report.txt"
    path.write_bytes(b"data")
    client = _client()
    with patch("lupaxa.discordit.client.requests.post", return_value=_response(204)) as post:
        assert client.send_file(str(path)) is True
    body = json.loads(post.call_args.kwargs["data"]["payload_json"])
    assert "content" not in body


def test_missing_file_raises() -> None:
    client = _client()
    with pytest.raises(ValueError, match="file not found"):
        client.send_file("/no/such/discordit-file")


def test_payload_values_win_over_defaults() -> None:
    client = _client(username="PyBot", tts=True)
    with patch("lupaxa.discordit.client.requests.post", return_value=_response(204)) as post:
        client.send_payload({"content": "hi", "username": "Other", "tts": False})
    body = post.call_args.kwargs["json"]
    assert body["username"] == "Other"
    assert body["tts"] is False


def test_content_limit() -> None:
    client = _client()
    with pytest.raises(ValueError, match="2000"):
        client.send_message("x" * 2001)


@pytest.mark.parametrize(
    ("status", "text", "match"),
    [
        (302, "", "please check your configuration"),
        (500, "", "Unknown error"),
        (400, "invalid_payload", "invalid_payload"),
    ],
)
def test_post_errors(status: int, text: str, match: str) -> None:
    client = _client()
    with (
        patch("lupaxa.discordit.client.requests.post", return_value=_response(status, text)),
        pytest.raises(ValueError, match=match) as exc,
    ):
        client.send_message("hi")
    assert "tokenvalue" not in str(exc.value)


def test_request_exception_propagates() -> None:
    client = _client()
    with (
        patch("lupaxa.discordit.client.requests.post", side_effect=requests.Timeout("slow")),
        pytest.raises(requests.Timeout),
    ):
        client.send_message("hi")


def test_validate_posts_content_username_and_avatar() -> None:
    client = _client(
        username="PyBot",
        avatar_url="https://example.com/a.png",
        tts=True,
        thread_name="Alerts",
        allowed_mentions={"parse": []},
    )
    with (
        patch("lupaxa.discordit.client.requests.get", return_value=_response(200)),
        patch("lupaxa.discordit.client.requests.post", return_value=_response(204)) as post,
    ):
        assert client.validate() is True
    body = post.call_args.kwargs["json"]
    assert body == {
        "content": "This is a validation message",
        "username": "PyBot",
        "avatar_url": "https://example.com/a.png",
    }


def test_validate_false_when_get_fails() -> None:
    client = _client()
    with patch.object(client, "valid_webhook", return_value=False) as probe:
        assert client.validate() is False
    probe.assert_called_once()


def test_timeout_must_be_positive() -> None:
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        _client(timeout=0)
