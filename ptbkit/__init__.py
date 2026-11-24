"""Small pieces shared by the militaernews Telegram bots (python-telegram-bot).

- `Strings`: translations from `res/strings/<lang>.json`, picked by the user's Telegram language
- `setup_logging`: console (and optional file) logging that keeps the bot token out of the logs
- `ErrorReporter`: posts unhandled errors to a log group topic
- `admin_ids`: parses a comma-separated list of Telegram user ids
- `ptbkit.check`: tests that every translation is complete (`assert_complete`, `python -m ptbkit.check`)
"""

from ptbkit.config import admin_ids
from ptbkit.errors import ErrorReporter, chat_id
from ptbkit.logs import setup_logging
from ptbkit.strings import Strings

__all__ = ["ErrorReporter", "Strings", "admin_ids", "chat_id", "setup_logging"]
__version__ = "0.2.0"
