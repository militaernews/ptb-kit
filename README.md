# ptb-kit

Small pieces shared by the [militaernews](https://github.com/militaernews) Telegram bots, built on
[python-telegram-bot](https://python-telegram-bot.org). No dependencies of its own; python-telegram-bot is
only needed for `Strings.apply_commands`.

```
pip install "ptbkit @ https://github.com/militaernews/ptb-kit/archive/refs/tags/v0.1.0.tar.gz"
```

## Translations: `Strings`

One JSON file per language in `res/strings/`. `en.json` has every key; other languages
(`de.json`, …) may leave keys out and fall back to English.

```
res/strings/en.json   {"welcome": "Hello {name}!", "command.help": "Show the help"}
res/strings/de.json   {"welcome": "Hallo {name}!", "command.help": "Hilfe anzeigen"}
```

```python
from ptbkit import Strings

strings = Strings("res/strings")

async def start(update, context):
    lang = strings.lang_of(update.effective_user)  # "de" for German clients, else "en"
    await update.message.reply_text(strings(lang, "welcome", name=update.effective_user.first_name))

# The command menu in every language, from the command.<name> keys
await strings.apply_commands(application.bot, ["help"])
```

`strings.missing()` and `strings.unknown()` list keys a translation lacks or has too many; assert on
them in a test so CI catches forgotten translations.

## Logging: `setup_logging`

```python
from ptbkit import setup_logging

log = setup_logging(file="logs/bot.log")  # file is optional
```

httpx logs every request URL at INFO, and Telegram's URLs contain the bot token; `setup_logging`
holds httpx at WARNING so the token stays out of logs and journals.

## Error reports: `ErrorReporter`

```python
from ptbkit import ErrorReporter

reporter = ErrorReporter("ptb-footer", chat_id=LOG_GROUP_ID, thread_id=THREAD_ID)
application.add_error_handler(reporter.handler())
```

Posts the error type, message and the last lines of the traceback to a log group topic (HTML-escaped,
within Telegram's length limit). The context names only the update type and chat id, so no message
contents end up in the log group. Without a `chat_id` it only logs. Reporting never raises.

## Admins: `admin_ids`

```python
from ptbkit import admin_ids

ADMINS = admin_ids(os.getenv("ADMIN_IDS"))  # "1, 2" → frozenset({1, 2})
```

## Development

```
pip install -e ".[telegram,test]"
pytest
```

MIT licensed.
