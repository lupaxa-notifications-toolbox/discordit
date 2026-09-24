# Getting Started

## Requirements

- Python 3.13 or newer
- A Discord incoming webhook URL you are allowed to post to
- `requests` and `PyYAML`, installed with the package

## Install

```bash
pip install lupaxa-discordit
discordit --help
```

## First Run

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --text "Hello"
```

The command exits `0` when Discord accepts the message. Put the webhook URL in
the environment, or in a profile, rather than in shell history.

## Config File

Profiles live in `$HOME/.discordit.yml`. Pass `--config` when the file lives
somewhere else. `--config` requires `--profile`.

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
`thread_name`, `allowed_mentions`, and `timeout`. A CLI flag overrides the
same field from the profile.

Module entry point:

```bash
python -m lupaxa.discordit --version
```

### From Source (Development)

```bash
make init
make python-install-dev
discordit --version
```

## Makefile Helpers

```bash
make init                 # clone makefile-skills into .makefiles/
make python-install-dev   # editable install with [dev]
make python-check         # lint + type + test
make mkdocs-serve         # local docs site
```
