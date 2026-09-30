<p align="center">
  <a href="https://github.com/lupaxa-notifications-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/notifications-toolbox/readme-logo.png" alt="Notifications Toolbox" />
  </a>
</p>

<h1 align="center">Discordit</h1>

Send Discord messages through an incoming webhook. Use it as a library or as
the `discordit` command. A successful post returns when Discord answers
HTTP 204.

## Install

Requires Python 3.13 or newer, and a Discord incoming webhook URL you are
allowed to post to.

```bash
pip install lupaxa-discordit
discordit --help
```

Put the webhook URL in the environment, or in a profile, rather than in
shell history.

## CLI

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --text "Hello"
discordit --profile testing --text "Hello"
discordit -p alerts --config "$HOME/work/discordit.yml" --text "Disk full"
discordit --webhook "$DISCORD_WEBHOOK_URL" --file report.txt --text "see attached"
discordit --webhook "$DISCORD_WEBHOOK_URL" --embed '{"title":"Hi"}' --tts
discordit --webhook "$DISCORD_WEBHOOK_URL" --thread-name Incident --text started
discordit --webhook "$DISCORD_WEBHOOK_URL" --allowed-mentions '{"parse":[]}' --text "no pings"
discordit --profile testing --validate
python -m lupaxa.discordit --version
```

The webhook URL must use Discord's
[`/api/webhooks/`](https://discord.com/developers/docs/resources/webhook)
path. Pass `--webhook`, or `--profile` with a `webhook_url` in the config
file.

`--text`, `--embed`, and `--file` may be combined. `--validate` cannot be
combined with them. One of those four is required. Flags override the same
fields from the selected profile. `--timeout` must be greater than `0`.

Escaped newlines in `--text` are sent as real line breaks, so `Hello\\nthere`
arrives as two lines. Content longer than 2000 characters is an error.
`--validate` probes the webhook, then posts `This is a validation message`
plus username and avatar when those are set. It does not send text-to-speech,
a thread name, or allowed mentions.

| Flag                 | Default             | Description                                   |
| :------------------- | :------------------ | :-------------------------------------------- |
| `--webhook`, `-w`    | profile value       | Discord webhook URL                           |
| `--profile`, `-p`    | —                   | Profile name in the config file               |
| `--config`           | `~/.discordit.yml`  | Config file path                              |
| `--text`, `-t`       | —                   | Message content                               |
| `--embed`            | —                   | One embed as a JSON object                    |
| `--file`             | —                   | One file path                                 |
| `--validate`         | —                   | Probe the URL, then post a validation message |
| `--username`, `-u`   | profile value       | Display name                                  |
| `--avatar-url`       | profile value       | Avatar URL                                    |
| `--tts` / `--no-tts` | profile, else false | Text-to-speech                                |
| `--thread-name`      | profile value       | Forum thread name                             |
| `--allowed-mentions` | profile value       | Allowed-mentions JSON object                  |
| `--timeout`, `-T`    | `10`                | Request timeout in seconds                    |
| `--version`          | —                   | Print the package version and exit            |

## Config

Profiles live in `$HOME/.discordit.yml`. Pass `--config` to use another
file. `--config` requires `--profile`.

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

The file must contain a `profiles` mapping. Unknown keys are rejected.

| Field              | Required                     | Meaning                                  |
| :----------------- | :--------------------------- | :--------------------------------------- |
| `webhook_url`      | unless `--webhook` is passed | Discord webhook URL                      |
| `username`         | no                           | Display name, 1–80 characters            |
| `avatar_url`       | no                           | Avatar URL                               |
| `tts`              | no                           | Text-to-speech; default false            |
| `thread_name`      | no                           | Forum thread name, 1–100 characters      |
| `allowed_mentions` | no                           | Allowed-mentions mapping                 |
| `timeout`          | no                           | Request timeout in seconds; default `10` |

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
client.send_embed('{"title": "Hello"}')
client.send_file("report.txt", content="see attached")
client.validate()
```

`send` is an alias of `send_message`. Username, avatar URL, text-to-speech,
thread name, and allowed mentions are added when you set them and the payload
does not already include that field. `send_payload` posts a JSON object, with
an optional file. A Discord HTTP 204 response returns `True`.

`load_profile` reads `$HOME/.discordit.yml` when no path is given. A missing
file, unknown profile, or invalid YAML raises `ConfigError`. `validate`
returns `False` when the probe does not succeed.

## Exit codes

| Code | When                                                         |
| :--- | :----------------------------------------------------------- |
| `0`  | Help, version, or Discord accepted the post                  |
| `1`  | The webhook was rejected, or the post failed                 |
| `2`  | Command-line usage, a bad config, or argument parsing failed |

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
