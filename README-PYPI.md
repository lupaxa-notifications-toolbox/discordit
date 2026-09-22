<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-notifications-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/notifications-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
</p>
<h3 align="center">
  The Lupaxa Notifications Toolbox<br />
  Part of The Lupaxa Project
</h3>

<br />

# lupaxa-discordit

Send Discord messages through an incoming webhook.

## Features

- Post message text, one embed, or one file
- Set a username and avatar URL on each client
- Keep several webhook profiles in `$HOME/.discordit.yml` and select one with `--profile`
- Override any profile field with a CLI flag
- Enable text-to-speech, a forum thread name, and allowed mentions
- Turn escaped `\n` sequences in message text into real line breaks
- Reject webhook URLs that do not start with `https://discord.com/api/webhooks/`
- Reject webhook URLs that answer `GET` with a redirect
- Use the `Discordit` library class or the `discordit` command

## Installation

### From PyPI

```bash
pip install lupaxa-discordit
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

Requires Python 3.13+. Runtime dependencies: `requests` and `PyYAML`.

## Library quick start

```python
from lupaxa.discordit import Discordit, load_profile

profile = load_profile("testing")
client = Discordit(
    profile.webhook_url,
    username=profile.username,
    avatar_url=profile.avatar_url,
)
client.send_message("Hello")
```

## CLI quick start

```bash
discordit --help
discordit --webhook "$DISCORD_WEBHOOK_URL" --text "Hello"
discordit --profile testing --text "Hello"
discordit -p alerts --config "$HOME/work/discordit.yml" --text "Disk full"
python -m lupaxa.discordit --version
```

The webhook URL must start with `https://discord.com/api/webhooks/`.
`--text`, `--embed`, and `--file` may be combined. `--validate` cannot
be combined with them. One of those four is required. Flags override
the same fields from the selected profile.

You can also run the CLI as a module:

```bash
python -m lupaxa.discordit --help
python -m lupaxa.discordit --version
```

## Config

Profiles live in one YAML file. The default path is `$HOME/.discordit.yml`.
Pass `--config` when the file lives somewhere else. `--config` requires
`--profile`. CLI flags override the selected profile.

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

Each profile may set `webhook_url`, `username`, `avatar_url`, `tts`,
`thread_name`, `allowed_mentions`, and `timeout`. `--webhook` is required
when you do not pass `--profile`.

## Development

Clone the repository and install with Make:

```bash
make init                # first-time makefile-skills checkout
make python-install-dev  # editable install with [dev]
make python-check        # lint, type-check, and test
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
