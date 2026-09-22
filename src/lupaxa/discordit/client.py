"""Discord incoming-webhook client."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import cast

import requests

DEFAULT_TIMEOUT = 10.0
WEBHOOK_PREFIX = "https://discord.com/api/webhooks/"
MAX_CONTENT = 2000
MAX_USERNAME = 80
MAX_THREAD_NAME = 100

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]

_MENTION_FIELDS = frozenset({"parse", "users", "roles", "replied_user"})
_PARSE_VALUES = frozenset({"roles", "users", "everyone"})
_REDIRECT_STATUSES = {301, 302}


def require_timeout(timeout: object) -> float:
    """Return ``timeout`` when it is finite and greater than 0."""
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("timeout must be a number")
    number = float(timeout)
    if not math.isfinite(number) or number <= 0:
        raise ValueError("timeout must be greater than 0")
    return number


def require_text(value: object, field: str, limit: int) -> str:
    """Return ``value`` when it is a non-empty string within ``limit``."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    if len(value) > limit:
        raise ValueError(f"{field} must be at most {limit} characters")
    return value


def parse_allowed_mentions(value: object) -> dict[str, JsonValue]:
    """Return a normalized allowed-mentions object or raise ``ValueError``."""
    if not isinstance(value, dict):
        raise ValueError("allowed_mentions must be an object")
    unknown = sorted(str(key) for key in value if key not in _MENTION_FIELDS)
    if unknown:
        raise ValueError(f"unknown allowed_mentions setting: {', '.join(unknown)}")
    parsed: dict[str, JsonValue] = {}
    if "parse" in value and value["parse"] is not None:
        parsed["parse"] = cast(JsonValue, _unique_tokens(value["parse"], "parse", _PARSE_VALUES))
    if "users" in value and value["users"] is not None:
        parsed["users"] = cast(JsonValue, _unique_ids(value["users"], "users"))
    if "roles" in value and value["roles"] is not None:
        parsed["roles"] = cast(JsonValue, _unique_ids(value["roles"], "roles"))
    if "replied_user" in value and value["replied_user"] is not None:
        flag = value["replied_user"]
        if not isinstance(flag, bool):
            raise ValueError("replied_user must be a boolean")
        parsed["replied_user"] = flag
    return parsed


def _unique_tokens(value: object, field: str, allowed: frozenset[str]) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    seen: list[str] = []
    for item in value:
        if not isinstance(item, str) or item not in allowed:
            raise ValueError(f"{field} entries must be roles, users, or everyone")
        if item not in seen:
            seen.append(item)
    return seen


def _unique_ids(value: object, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    seen: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{field} entries must be non-empty strings")
        if item not in seen:
            seen.append(item)
    return seen


class Discordit:
    """Send messages through a Discord incoming webhook."""

    def __init__(
        self,
        webhook_url: str,
        *,
        username: str | None = None,
        avatar_url: str | None = None,
        tts: bool = False,
        thread_name: str | None = None,
        allowed_mentions: dict[str, JsonValue] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Store webhook settings after the URL passes validation."""
        if not webhook_url:
            raise ValueError("Webhook URL required")
        if not webhook_url.startswith(WEBHOOK_PREFIX):
            raise ValueError(f"Invalid webhook URL - should start with {WEBHOOK_PREFIX}")
        self.webhook_url = webhook_url
        self.username = (
            None if username is None else require_text(username, "username", MAX_USERNAME)
        )
        self.avatar_url = (
            None if avatar_url is None else require_text(avatar_url, "avatar_url", 10**6)
        )
        if not isinstance(tts, bool):
            raise ValueError("tts must be a boolean")
        self.tts = tts
        self.thread_name = (
            None
            if thread_name is None
            else require_text(thread_name, "thread_name", MAX_THREAD_NAME)
        )
        self.allowed_mentions = (
            None if allowed_mentions is None else parse_allowed_mentions(allowed_mentions)
        )
        self.timeout = require_timeout(timeout)
        if not self.valid_webhook(self.webhook_url):
            raise ValueError(_invalid_webhook(self.webhook_url))

    def valid_webhook(self, url: str) -> bool:
        """Return whether ``url`` answers without a redirect."""
        try:
            response = requests.get(url, allow_redirects=False, timeout=self.timeout)
        except requests.RequestException:
            return False
        return response.status_code not in _REDIRECT_STATUSES

    def send_message(self, content: str) -> bool:
        """Post ``content``, turning escaped newlines into real line breaks."""
        return self.send_payload({"content": content})

    def send(self, content: str) -> bool:
        """Post ``content``. Alias of ``send_message``."""
        return self.send_message(content)

    def send_embed(self, embed: str) -> bool:
        """Post one embed encoded as a JSON object string."""
        parsed = self.convert_to_json(embed)
        if not isinstance(parsed, dict):
            raise ValueError("embed must be a JSON object")
        return self.send_payload({"embeds": [parsed]})

    def send_file(self, file_path: str, content: str | None = None) -> bool:
        """Post one file. ``content`` is omitted when it is ``None``."""
        payload: dict[str, JsonValue] = {}
        if content is not None:
            payload["content"] = content
        return self.send_payload(payload, file_path=file_path)

    def convert_to_json(self, json_string: str) -> JsonValue:
        """Parse ``json_string`` or raise ``ValueError``."""
        try:
            parsed = json.loads(json_string)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid json") from exc
        return cast(JsonValue, parsed)

    def send_payload(
        self,
        payload: dict[str, JsonValue],
        *,
        file_path: str | None = None,
    ) -> bool:
        """POST ``payload``. A file is sent as multipart ``payload_json``."""
        body = _with_defaults(
            payload,
            self.username,
            self.avatar_url,
            self.tts,
            self.thread_name,
            self.allowed_mentions,
        )
        return self._post(body, file_path)

    def validate(self) -> bool:
        """Probe the webhook, then post a validation message."""
        if not self.valid_webhook(self.webhook_url):
            return False
        body: dict[str, JsonValue] = {"content": "This is a validation message"}
        if self.username is not None:
            body["username"] = self.username
        if self.avatar_url is not None:
            body["avatar_url"] = self.avatar_url
        self._post(body, None)
        return True

    def _post(self, body: dict[str, JsonValue], file_path: str | None) -> bool:
        body = dict(body)
        content = body.get("content")
        if isinstance(content, str):
            normalized = content.replace("\\n", "\n")
            body["content"] = normalized
            if len(normalized) > MAX_CONTENT:
                raise ValueError(f"content must be at most {MAX_CONTENT} characters")
        if file_path is None:
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                json=body,
                timeout=self.timeout,
                allow_redirects=False,
            )
        else:
            path = Path(file_path)
            if not path.is_file():
                raise ValueError(f"file not found: {file_path}")
            with path.open("rb") as handle:
                response = requests.post(
                    self.webhook_url,
                    data={"payload_json": json.dumps(body)},
                    files={"files[0]": (path.name, handle)},
                    timeout=self.timeout,
                    allow_redirects=False,
                )
        return _raise_for_status(response, self.webhook_url)


def _with_defaults(
    payload: dict[str, JsonValue],
    username: str | None,
    avatar_url: str | None,
    tts: bool,
    thread_name: str | None,
    allowed_mentions: dict[str, JsonValue] | None,
) -> dict[str, JsonValue]:
    body = dict(payload)
    for key, value in (
        ("username", username),
        ("avatar_url", avatar_url),
        ("thread_name", thread_name),
        ("allowed_mentions", allowed_mentions),
    ):
        if key not in body and value is not None:
            body[key] = value
    if "tts" not in body and tts:
        body["tts"] = True
    return body


def _raise_for_status(response: requests.Response, webhook_url: str) -> bool:
    if response.status_code == 204:
        return True
    if response.status_code in _REDIRECT_STATUSES:
        raise ValueError(_invalid_webhook(webhook_url))
    if not response.text:
        raise ValueError(f"Unknown error for webhook {_webhook_id(webhook_url)}")
    raise ValueError(response.text)


def _invalid_webhook(webhook_url: str) -> str:
    return (
        f"Invalid webhook URL for webhook {_webhook_id(webhook_url)}"
        " - please check your configuration"
    )


def _webhook_id(webhook_url: str) -> str:
    rest = webhook_url.removeprefix(WEBHOOK_PREFIX)
    webhook_id = rest.split("/", 1)[0]
    return webhook_id or "webhook"
