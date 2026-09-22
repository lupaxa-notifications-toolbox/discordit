<p align="center">
  <a href="https://github.com/lupaxa-notifications-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/notifications-toolbox/readme-logo.png" alt="Notifications Toolbox" />
  </a>
</p>

<h1 align="center">discordit</h1>

Send Discord messages through an incoming webhook.

<p align="center">
  <a href="https://discordit.thelupaxaproject.org/">Documentation</a>
  ·
  <a href="https://github.com/lupaxa-notifications-toolbox/discordit">GitHub</a>
</p>

## Install

```bash
pip install lupaxa-discordit
discordit --help
```

## CLI

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --text "Hello"
discordit --profile testing --text "Hello"
discordit -p alerts --config "$HOME/work/discordit.yml" --text "Disk full"
python -m lupaxa.discordit --version
```

The webhook URL must start with `https://discord.com/api/webhooks/`.
`--text`, `--embed`, and `--file` may be combined. `--validate` cannot
be combined with them. One of those four is required. Flags override
the same fields from the selected profile.

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

Each profile may set `webhook_url`, `username`, `avatar_url`, `tts`,
`thread_name`, `allowed_mentions`, and `timeout`.

## Library

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

## Development

```bash
make init
make python-install-dev
make python-check
make mkdocs-serve
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
