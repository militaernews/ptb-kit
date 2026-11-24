"""Small pieces shared by the militaernews Telegram bots (python-telegram-bot).

- `Strings`: translations from `res/strings/<lang>.json`, picked by the user's Telegram language
- `setup_logging`: console (and optional file) logging that keeps the bot token out of the logs
- `ErrorReporter`: posts unhandled errors to a log group topic
- `admin_ids`: parses a comma-separated list of Telegram user ids
"""

from ptbkit.config import admin_ids
from ptbkit.errors import ErrorReporter
from ptbkit.logs import setup_logging
from ptbkit.strings import Strings

__all__ = ["ErrorReporter", "Strings", "admin_ids", "setup_logging"]
__version__ = "0.1.0"
