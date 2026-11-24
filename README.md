<p align="center"><img src="brand/logo.png" alt="ptb-kit: a toolkit case on a radar screen" width="200"></p>

# ptb-kit

Small pieces shared by the [militaernews](https://github.com/militaernews) Telegram bots, built on
[python-telegram-bot](https://python-telegram-bot.org). No dependencies of its own; python-telegram-bot is
only needed for `Strings.apply_commands`.

```
pip install "ptbkit @ https://github.com/militaernews/ptb-kit/archive/refs/tags/v0.2.0.tar.gz"
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

`apply_commands` takes a `scope` (e.g. `BotCommandScopeChat(admin_id)`) for menus only some chats see.

## Testing translations: `ptbkit.check`

One test catches every forgotten or broken translation:

```python
from ptbkit.check import assert_complete
from bot.strings import strings

def test_translations():
    assert_complete(strings, code="bot")   # the folder with the bot's Python code
```

or in CI without a test file: `python -m ptbkit.check bot/res/strings bot`. It reports:

- keys a language lacks, or has that `en.json` doesn't
- texts whose `{placeholders}` differ from English, and texts that aren't valid format strings
- keys the code uses (`t(lang, "key")`, `strings(lang, "key")`, `strings.get(lang, "key")` …) that
  `en.json` doesn't have
- keys nothing uses (switch off with `unused=False`; prefixes the code builds at runtime, such as
  `command.` and `label.`, are skipped; set others with `dynamic=(...)`)

For other call styles pass your own regex with a `key` group as `call=`.

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

The group id may be given as `-100…` or as the bare number some clients show; `chat_id()` does the
same conversion for your own messages. Posts the error type, message and the last lines of the traceback to a log group topic (HTML-escaped,
within Telegram's length limit). The context names only the update type and chat id, so no message
contents end up in the log group. Without a `chat_id` it only logs. Reporting never raises.

## Admins: `admin_ids`

```python
from ptbkit import admin_ids

ADMINS = admin_ids(os.getenv("ADMIN_IDS"))  # "1, 2" → frozenset({1, 2})
```

## Logo

`brand/brand.json`, drawn with the brand generator from [militaernews/tools](https://github.com/militaernews/tools).

## Development

```
pip install -e ".[telegram,test]"
pytest
```

MIT licensed.
