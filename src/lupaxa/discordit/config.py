"""Load Discordit profiles from a YAML config file."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from .client import (
    DEFAULT_TIMEOUT,
    MAX_THREAD_NAME,
    MAX_USERNAME,
    JsonValue,
    parse_allowed_mentions,
    require_text,
    require_timeout,
)

_PROFILE_FIELDS = (
    "webhook_url",
    "username",
    "avatar_url",
    "tts",
    "thread_name",
    "allowed_mentions",
    "timeout",
)


class ConfigError(ValueError):
    """The config file or selected profile cannot be used."""


@dataclass(frozen=True)
class Profile:
    """One named block of webhook settings from the config file."""

    webhook_url: str | None = None
    username: str | None = None
    avatar_url: str | None = None
    tts: bool | None = None
    thread_name: str | None = None
    allowed_mentions: dict[str, JsonValue] | None = None
    timeout: float | None = None


@dataclass(frozen=True)
class ResolvedSettings:
    """Webhook settings after CLI flags override a profile."""

    webhook_url: str
    username: str | None
    avatar_url: str | None
    tts: bool
    thread_name: str | None
    allowed_mentions: dict[str, JsonValue] | None
    timeout: float


def default_config_path() -> Path:
    """Return the default config path, ``$HOME/.discordit.yml``."""
    return Path.home() / ".discordit.yml"


def load_profile(name: str, path: Path | None = None) -> Profile:
    """Load ``name`` from ``path`` or from ``$HOME/.discordit.yml``."""
    config_path = default_config_path() if path is None else path
    if not config_path.is_file():
        raise ConfigError(f"config file not found: {config_path}")
    try:
        loaded: object = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid config file: {config_path}") from exc
    profiles = _profiles(loaded, config_path)
    if name not in profiles:
        raise ConfigError(f"profile not found: {name}")
    raw = profiles[name]
    if not isinstance(raw, dict):
        raise ConfigError(f"profile {name} must be a mapping")
    unknown = sorted(str(key) for key in raw if key not in _PROFILE_FIELDS)
    if unknown:
        raise ConfigError(f"unknown profile setting: {', '.join(unknown)}")
    return Profile(
        webhook_url=_optional_text(raw.get("webhook_url"), "webhook_url"),
        username=_optional_bounded(raw.get("username"), "username", MAX_USERNAME),
        avatar_url=_optional_text(raw.get("avatar_url"), "avatar_url"),
        tts=_optional_bool(raw.get("tts"), "tts"),
        thread_name=_optional_bounded(raw.get("thread_name"), "thread_name", MAX_THREAD_NAME),
        allowed_mentions=_optional_mentions(raw.get("allowed_mentions")),
        timeout=_optional_timeout(raw.get("timeout")),
    )


def resolve_settings(
    *,
    profile_name: str | None,
    config_path: Path | None,
    webhook_url: str | None,
    username: str | None,
    avatar_url: str | None,
    tts: bool | None,
    thread_name: str | None,
    allowed_mentions: str | None,
    timeout: float | None,
) -> ResolvedSettings:
    """Merge CLI values over an optional profile.

    A passed CLI value wins. ``timeout`` falls back to ``DEFAULT_TIMEOUT``.
    ``tts`` falls back to false. ``allowed_mentions`` is a JSON object string.
    """
    if profile_name is None and config_path is not None:
        raise ConfigError("--profile is required when --config is set")
    profile = load_profile(profile_name, config_path) if profile_name else None
    resolved_webhook = _pick(webhook_url, None if profile is None else profile.webhook_url)
    if not resolved_webhook:
        raise ConfigError("webhook URL required")
    if tts is not None:
        resolved_tts = tts
    elif profile is not None and profile.tts is not None:
        resolved_tts = profile.tts
    else:
        resolved_tts = False
    if timeout is not None:
        resolved_timeout = require_timeout(timeout)
    elif profile is not None and profile.timeout is not None:
        resolved_timeout = profile.timeout
    else:
        resolved_timeout = DEFAULT_TIMEOUT
    mentions = (
        _mentions_json(allowed_mentions)
        if allowed_mentions is not None
        else None
        if profile is None
        else profile.allowed_mentions
    )
    return ResolvedSettings(
        webhook_url=resolved_webhook,
        username=_pick_text(
            username,
            None if profile is None else profile.username,
            "username",
            MAX_USERNAME,
        ),
        avatar_url=_pick_text(
            avatar_url,
            None if profile is None else profile.avatar_url,
            "avatar_url",
            None,
        ),
        tts=resolved_tts,
        thread_name=_pick_text(
            thread_name,
            None if profile is None else profile.thread_name,
            "thread_name",
            MAX_THREAD_NAME,
        ),
        allowed_mentions=mentions,
        timeout=resolved_timeout,
    )


def _pick(cli_value: str | None, profile_value: str | None) -> str | None:
    return cli_value if cli_value is not None else profile_value


def _pick_text(
    cli_value: str | None,
    profile_value: str | None,
    field: str,
    limit: int | None,
) -> str | None:
    chosen = _pick(cli_value, profile_value)
    if chosen is None:
        return None
    if limit is None:
        return require_text(chosen, field, 10**6)
    return require_text(chosen, field, limit)


def _profiles(loaded: object, config_path: Path) -> dict[object, object]:
    if not isinstance(loaded, dict):
        raise ConfigError(f"invalid config file: {config_path}")
    unknown = sorted(str(key) for key in loaded if key != "profiles")
    if unknown:
        raise ConfigError(f"unknown config setting: {', '.join(unknown)}")
    profiles = loaded.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ConfigError("config file must define profiles")
    for name in profiles:
        if not isinstance(name, str) or not name:
            raise ConfigError("profile names must be strings")
    return profiles


def _optional_text(value: object, field: str) -> str | None:
    if value is None:
        return None
    try:
        return require_text(value, field, 10**6)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc


def _optional_bounded(value: object, field: str, limit: int) -> str | None:
    if value is None:
        return None
    try:
        return require_text(value, field, limit)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc


def _optional_bool(value: object, field: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ConfigError(f"{field} must be a boolean")
    return value


def _optional_mentions(value: object) -> dict[str, JsonValue] | None:
    if value is None:
        return None
    try:
        return parse_allowed_mentions(value)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc


def _optional_timeout(value: object) -> float | None:
    if value is None:
        return None
    try:
        return require_timeout(value)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc


def _mentions_json(text: str) -> dict[str, JsonValue]:
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid json") from exc
    return parse_allowed_mentions(loaded)
