"""Command-line interface for Discordit."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests

from .client import DEFAULT_TIMEOUT, Discordit, JsonValue, require_timeout
from .config import ConfigError, resolve_settings
from .version import get_version


def _positive_timeout(value: str) -> float:
    try:
        return require_timeout(float(value))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _exit_code(exc: SystemExit) -> int:
    code = exc.code
    if code is None:
        return 0
    return code if isinstance(code, int) else 1


def _program_name(argv0: str) -> str:
    name = os.path.basename(argv0)
    return "discordit" if name == "__main__.py" else name


def build_parser() -> argparse.ArgumentParser:
    """Build the ``discordit`` argument parser."""
    parser = argparse.ArgumentParser(
        description="Send a Discord message through an incoming webhook.",
    )
    parser.add_argument("-w", "--webhook", default=None, metavar="URL", help="Discord webhook URL")
    parser.add_argument("-p", "--profile", default=None, metavar="NAME", help="Profile name")
    parser.add_argument(
        "--config",
        default=None,
        metavar="PATH",
        help="Config file (default: ~/.discordit.yml)",
    )
    parser.add_argument("-u", "--username", default=None, help="Display name")
    parser.add_argument("--avatar-url", default=None, help="Avatar URL")
    tts = parser.add_mutually_exclusive_group()
    tts.add_argument("--tts", dest="tts_flag", action="store_const", const=True, help="Enable TTS")
    tts.add_argument(
        "--no-tts", dest="tts_flag", action="store_const", const=False, help="Disable TTS"
    )
    parser.set_defaults(tts_flag=None)
    parser.add_argument("--thread-name", default=None, help="Forum thread name")
    parser.add_argument("--allowed-mentions", default=None, help="Allowed mentions JSON object")
    parser.add_argument(
        "-T",
        "--timeout",
        type=_positive_timeout,
        default=None,
        metavar="SECONDS",
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT:g})",
    )
    parser.add_argument("-t", "--text", default=None, help="Message content")
    parser.add_argument("--embed", default=None, help="One embed as a JSON object")
    parser.add_argument("--file", default=None, help="File to upload")
    parser.add_argument("--validate", action="store_true", help="Send a validation message")
    parser.add_argument("--version", action="version", version=get_version())
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return _exit_code(exc)
    has_payload = args.text is not None or args.embed is not None or args.file is not None
    try:
        if args.validate and has_payload:
            parser.error("--validate cannot be combined with --text, --embed, or --file")
        if not args.validate and not has_payload:
            parser.error("one of --text, --embed, --file, or --validate is required")
    except SystemExit as exc:
        return _exit_code(exc)
    config_path = Path(args.config).expanduser() if args.config else None
    try:
        settings = resolve_settings(
            profile_name=args.profile,
            config_path=config_path,
            webhook_url=args.webhook,
            username=args.username,
            avatar_url=args.avatar_url,
            tts=args.tts_flag,
            thread_name=args.thread_name,
            allowed_mentions=args.allowed_mentions,
            timeout=args.timeout,
        )
        client = Discordit(
            settings.webhook_url,
            username=settings.username,
            avatar_url=settings.avatar_url,
            tts=settings.tts,
            thread_name=settings.thread_name,
            allowed_mentions=settings.allowed_mentions,
            timeout=settings.timeout,
        )
        if args.validate:
            if not client.validate():
                print(f"{_program_name(sys.argv[0])}: invalid webhook URL", file=sys.stderr)
                return 1
            return 0
        payload: dict[str, JsonValue] = {}
        if args.text is not None:
            payload["content"] = args.text
        if args.embed is not None:
            parsed = client.convert_to_json(args.embed)
            if not isinstance(parsed, dict):
                raise ValueError("embed must be a JSON object")
            payload["embeds"] = [parsed]
        client.send_payload(payload, file_path=args.file)
    except ConfigError as exc:
        print(f"{_program_name(sys.argv[0])}: {exc}", file=sys.stderr)
        return 2
    except (ValueError, requests.RequestException) as exc:
        print(f"{_program_name(sys.argv[0])}: {exc}", file=sys.stderr)
        return 1
    return 0
