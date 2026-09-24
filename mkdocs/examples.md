# Examples

## Plain Text

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --text "Hello"
```

## Profile

```bash
discordit --profile testing --text "Hello"
```

## Config Path

```bash
discordit -p alerts --config "$HOME/work/discordit.yml" --text "Disk full"
```

## File Plus Text

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --file report.txt --text "see attached"
```

## Embed Plus TTS

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --embed '{"title":"Hi"}' --tts
```

## Thread Name

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --thread-name Incident --text started
```

## Allowed Mentions

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --allowed-mentions '{"parse":[]}' --text "no pings"
```

## Validation Post

```bash
discordit --profile testing --validate
```

This probes the webhook, then posts `This is a validation message` plus
username and avatar when set.

## Version

```bash
python -m lupaxa.discordit --version
```
