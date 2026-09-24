# Reference

## CLI Arguments

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

The webhook URL must use Discord's
[`/api/webhooks/`](https://discord.com/developers/docs/resources/webhook)
path.
`--timeout` must be greater than `0`. At least one of `--text`, `--embed`,
`--file`, or `--validate` is required. `--validate` cannot be combined with
`--text`, `--embed`, or `--file`. Pass `--webhook`, or `--profile` with a
`webhook_url` in the config file. `--config` selects a file other than
`$HOME/.discordit.yml` and requires `--profile`. CLI flags override the
selected profile.

## Config File

The default path is `$HOME/.discordit.yml`, from `default_config_path()`.
`--config` selects another file and requires `--profile`.

| Field              | Required                         | Meaning                                      |
| :----------------- | :------------------------------- | :------------------------------------------- |
| `webhook_url`      | unless `--webhook` is passed     | Discord webhook URL                          |
| `username`         | no                               | Display name, 1–80 characters                |
| `avatar_url`       | no                               | Avatar URL                                   |
| `tts`              | no                               | Text-to-speech; default false                |
| `thread_name`      | no                               | Forum thread name, 1–100 characters          |
| `allowed_mentions` | no                               | Allowed-mentions mapping                     |
| `timeout`          | no                               | Request timeout in seconds; default `10`     |

The file must contain a `profiles` mapping. Profile names are strings.
Unknown keys are rejected. CLI flags override the selected profile.

## Exit Codes

| Code | When                                                         |
| :--- | :----------------------------------------------------------- |
| `0`  | Help, version, or Discord accepted the post                  |
| `1`  | The webhook was rejected, or the post failed                 |
| `2`  | Command-line usage, a bad config, or argument parsing failed |

## Library

| Name                  | Meaning                                                                 |
| :-------------------- | :---------------------------------------------------------------------- |
| `Discordit`           | Client bound to one incoming webhook                                    |
| `send_message`        | Post text, unescaping `\\n`                                             |
| `send`                | Alias of `send_message`                                                 |
| `send_embed`          | Post one embed from a JSON object string                                |
| `send_file`           | Post one file; optional content text                                    |
| `send_payload`        | POST a JSON object, filling username, avatar, TTS, thread, and mentions |
| `validate`            | GET the webhook, then post a validation message                         |
| `DEFAULT_TIMEOUT`     | Default request timeout (`10.0`)                                        |
| `WEBHOOK_PREFIX`      | Required URL prefix                                                     |
| `load_profile`        | Load one named profile from a YAML config file                          |
| `default_config_path` | Return `$HOME/.discordit.yml`                                           |
| `ConfigError`         | Raised when the config file or profile cannot be used                   |
| `Profile`             | Webhook settings stored for one profile                                 |
| `get_version()`       | Return the package version string                                       |
| `__version__`         | Package version string                                                  |

`validate` posts `This is a validation message` plus username and avatar when
set. It does not send TTS, thread name, or allowed mentions. A Discord HTTP
204 response returns `True`. Redirects, an empty error body, Discord error
text, and invalid JSON raise `ValueError`. Network failures raise the
underlying `requests` exception. `validate` returns `False` when the probe
does not succeed.
