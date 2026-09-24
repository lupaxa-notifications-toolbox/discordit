# Usage

Use `discordit` to post text, one embed, and one file together in a single
execute call. Pass the webhook URL with `--webhook`, or select a profile with
`--profile`.

## CLI Flags

| Flag                      | Default              | Description                                      |
| :------------------------ | :------------------- | :----------------------------------------------- |
| `--webhook`, `-w`         | profile value        | Discord webhook URL                              |
| `--profile`, `-p`         | —                    | Profile name in the config file                  |
| `--config`                | `~/.discordit.yml`   | Config file path                                 |
| `--text`, `-t`            | —                    | Message content                                  |
| `--embed`                 | —                    | One embed as a JSON object                       |
| `--file`                  | —                    | One file path                                    |
| `--validate`              | —                    | Probe the URL, then post a validation message    |
| `--username`, `-u`        | profile value        | Display name                                     |
| `--avatar-url`            | profile value        | Avatar URL                                       |
| `--tts` / `--no-tts`      | profile, else false  | Text-to-speech                                   |
| `--thread-name`           | profile value        | Forum thread name                                |
| `--allowed-mentions`      | profile value        | Allowed-mentions JSON object                     |
| `--timeout`, `-T`         | `10`                 | Request timeout in seconds                       |
| `--version`               | —                    | Print the package version and exit               |

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --username PyBot --text "Hello"
```

`--text`, `--embed`, and `--file` may be combined. At least one of those three,
or `--validate`, is required. `--validate` cannot be combined with `--text`,
`--embed`, or `--file`. `--timeout` must be greater than `0`. A flag overrides
the same field from the selected profile.

Escaped newlines in `--text` are sent as real line breaks, so `Hello\\nthere`
arrives as two lines. Content longer than 2000 characters is an error.

## Config File

Profiles live in one YAML file. The default path is `$HOME/.discordit.yml`.
Pass `--config` when the file lives somewhere else.

```yaml
profiles:
  testing:
    webhook_url: https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN
    username: PyBot
    avatar_url: https://example.com/avatar.png
    tts: false
    thread_name: Alerts
    allowed_mentions:
      parse: []
    timeout: 15
```

```bash
discordit --profile testing --text "Hello"
discordit -p alerts --config "$HOME/work/discordit.yml" --text "Disk full"
```

Each profile may set `webhook_url`, `username`, `avatar_url`, `tts`,
`thread_name`, `allowed_mentions`, and `timeout`. Other keys are rejected.
`--webhook` is still required when you do not pass `--profile`. `--config`
requires `--profile`.

## Library

```python
from lupaxa.discordit import Discordit, load_profile

profile = load_profile("testing")
client = Discordit(
    profile.webhook_url,
    username=profile.username,
    avatar_url=profile.avatar_url,
    tts=profile.tts or False,
    thread_name=profile.thread_name,
    allowed_mentions=profile.allowed_mentions,
    timeout=profile.timeout or 10.0,
)
client.send_message("Hello from a profile")

client = Discordit(
    "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN",
    username="PyBot",
    avatar_url="https://example.com/avatar.png",
    timeout=10.0,
)
client.send_message("Hello, Discord!")
client.send("Hello, Discord!")
client.send_embed('{"title": "Hello"}')
client.send_file("report.txt", content="see attached")
```

`JsonValue` is a JSON string, number, boolean, null, list, or object. `send`
is an alias of `send_message`. Username, avatar URL, TTS, thread name, and
allowed mentions are added to the JSON body when you set them and the payload
does not already include that field. `validate` probes the webhook again and
posts `This is a validation message` plus username and avatar when set. It
does not send TTS, thread name, or allowed mentions.

Signatures:

```python
Discordit(
    webhook_url: str,
    *,
    username: str | None = None,
    avatar_url: str | None = None,
    tts: bool = False,
    thread_name: str | None = None,
    allowed_mentions: dict[str, JsonValue] | None = None,
    timeout: float = 10.0,
)

send_message(content: str) -> bool
send(content: str) -> bool
send_embed(embed: str) -> bool
send_file(file_path: str, content: str | None = None) -> bool
send_payload(payload: dict[str, JsonValue], *, file_path: str | None = None) -> bool
validate() -> bool

load_profile(name: str, path: Path | None = None) -> Profile
```

`load_profile` reads `$HOME/.discordit.yml` when `path` is omitted. A missing
file, unknown profile, or invalid YAML raises `ConfigError`.
