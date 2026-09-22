"""lupaxa.discordit — send Discord messages through an incoming webhook."""

from __future__ import annotations

from .client import DEFAULT_TIMEOUT, WEBHOOK_PREFIX, Discordit
from .config import ConfigError, Profile, default_config_path, load_profile
from .version import __version__, get_version

__all__ = [
    "DEFAULT_TIMEOUT",
    "WEBHOOK_PREFIX",
    "ConfigError",
    "Discordit",
    "Profile",
    "__version__",
    "default_config_path",
    "get_version",
    "load_profile",
]
