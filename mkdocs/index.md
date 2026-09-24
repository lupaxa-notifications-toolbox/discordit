# Discordit

`lupaxa-discordit` posts messages to Discord through an incoming webhook. Use it as
a library or as the `discordit` command.

```bash
pip install lupaxa-discordit
discordit --webhook "$DISCORD_WEBHOOK_URL" --text "Hello"
discordit --profile testing --text "Hello"
```

A successful post returns when Discord answers HTTP 204. The webhook URL must
use Discord's
[`/api/webhooks/`](https://discord.com/developers/docs/resources/webhook)
path. `--profile` reads a named
profile from `$HOME/.discordit.yml`.
