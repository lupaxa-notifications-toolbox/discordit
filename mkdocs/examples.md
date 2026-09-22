# Examples

## Plain text

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --text "Hello"
```

## Profile

```bash
discordit --profile testing --text "Hello"
```

## Config path

```bash
discordit -p alerts --config "$HOME/work/discordit.yml" --text "Disk full"
```

## File plus text

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --file report.txt --text "see attached"
```

## Embed plus TTS

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --embed '{"title":"Hi"}' --tts
```

## Thread name

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --thread-name Incident --text started
```

## Allowed mentions

```bash
discordit --webhook "$DISCORD_WEBHOOK_URL" --allowed-mentions '{"parse":[]}' --text "no pings"
```

## Validation post

```bash
discordit --profile testing --validate
```

This probes the webhook, then posts `This is a validation message` plus
username and avatar when set.

## Version

```bash
python -m lupaxa.discordit --version
```
